from __future__ import annotations

import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "read_research_pdf.py"
SPEC = importlib.util.spec_from_file_location("read_research_pdf", SCRIPT)
PDF = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PDF)


def document(pages):
    """Tiny valid PDF fixture; separate physical pages, optional empty layer."""
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               ("<< /Type /Pages /Count %d /Kids [%s] >>" % (
                   len(pages), " ".join(f"{4+2*i} 0 R" for i in range(len(pages))))).encode(),
               b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    for i, text in enumerate(pages):
        objects.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 300] "
                        "/Resources << /Font << /F1 3 0 R >> >> /Contents %d 0 R >>" % (5+2*i)).encode())
        content = f"BT /F1 12 Tf 20 250 Td ({text}) Tj ET".encode() if text else b""
        objects.append(f"<< /Length {len(content)} >>\nstream\n".encode()+content+b"\nendstream")
    data=b"%PDF-1.4\n"
    offsets=[0]
    for i,obj in enumerate(objects,1):
        offsets.append(len(data))
        data+=f"{i} 0 obj\n".encode()+obj+b"\nendobj\n"
    xref=len(data)
    data+=f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode()
    data+=b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:])
    return data+f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()


class Handler(BaseHTTPRequestHandler):
    requests=[]

    def log_message(self, *args):
        pass

    def do_GET(self):
        type(self).requests.append((self.path,self.headers.get('User-Agent')))
        if self.path=='/redirect':
            self.send_response(302)
            self.send_header('Location','/call%20notes.pdf')
            self.end_headers()
            return
        status=200
        body=document(['Prepared remarks: USD million','Q and A: capital payback'])
        if self.path=='/denied' or self.headers.get('User-Agent','').startswith('curl/'):
            status,body=403,b'User agent denied'
        elif self.path=='/html.pdf':
            body=b'<html>Login required</html>'
        elif self.path=='/partial':
            status=206
        self.send_response(status)
        self.send_header('Content-Type','application/octet-stream')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@unittest.skipUnless(shutil.which('curl') and shutil.which('pdftotext'), 'requires curl and Poppler')
class ReadResearchPdfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def test_default_client_failure_and_identified_get_recovers_original_pages(self):
        baseline=subprocess.run(['curl','-s','-o','/dev/null','-w','%{http_code}',self.url+'/call%20notes.pdf'],capture_output=True,text=True)
        self.assertEqual(baseline.stdout,'403')
        result=PDF.read_pdf(self.url+'/call notes.pdf',self.root)
        self.assertEqual(result['status'],'text_extracted')
        self.assertEqual(result['page_count'],2)
        text=Path(result['text_file']).read_text()
        self.assertIn('## PDF page 2',text)
        self.assertIn('capital payback',text)
        self.assertEqual(Handler.requests[-1],('/call%20notes.pdf',PDF.USER_AGENT))
        self.assertEqual(json.loads((Path(result['artifact_dir'])/'manifest.json').read_text())['sha256'],result['sha256'])

    def test_redirect_keeps_requested_and_final_sources(self):
        result=PDF.read_pdf(self.url+'/redirect',self.root)
        self.assertEqual(result['status'],'text_extracted')
        self.assertTrue(result['source'].endswith('/redirect'))
        self.assertTrue(result['final_url'].endswith('/call%20notes.pdf'))

    def test_html_with_200_is_not_a_pdf(self):
        result=PDF.read_pdf(self.url+'/html.pdf',self.root)
        self.assertEqual(result['status'],'not_pdf')
        self.assertNotIn('text_file',result)
        self.assertFalse((Path(result['artifact_dir'])/'source.pdf').exists())

    def test_denied_and_partial_download_are_not_retried_or_accepted(self):
        for path in ('/denied','/partial'):
            count=len(Handler.requests)
            result=PDF.read_pdf(self.url+path,self.root)
            self.assertEqual(result['status'],'fetch_failed')
            self.assertEqual(len(Handler.requests),count+1)
            self.assertNotIn('text_file',result)

    def test_scan_and_mixed_pages_are_flagged(self):
        for pages,status,blank in [(['',''],'needs_ocr',[1,2]),(['Statement',''],'partial_text',[2])]:
            path=self.root/'scan.pdf'
            path.write_bytes(document(pages))
            result=PDF.read_pdf(str(path),self.root)
            self.assertEqual(result['status'],status)
            self.assertEqual(result['empty_pages'],blank)

    def test_corrupt_pdf_is_a_parse_failure_not_an_empty_scan(self):
        path=self.root/'bad.pdf'
        path.write_bytes(b'%PDF-1.7\ntruncated')
        result=PDF.read_pdf(str(path),self.root)
        self.assertEqual(result['status'],'parse_failed')
        self.assertTrue(Path(result['pdf_file']).exists())

    def test_missing_parser_keeps_pdf_and_repeated_calls_do_not_overwrite(self):
        path=self.root/'original.pdf'
        data=document(['Original'])
        path.write_bytes(data)
        with patch.object(PDF.shutil,'which',return_value=None):
            result=PDF.read_pdf(str(path),self.root)
        self.assertEqual(result['status'],'parser_unavailable')
        second=PDF.read_pdf(str(path),self.root)
        self.assertNotEqual(result['artifact_dir'],second['artifact_dir'])
        self.assertEqual(path.read_bytes(),data)

    def test_url_encoding_is_idempotent_and_credentials_rejected(self):
        url=self.url+'/call%20notes.pdf?name=Some%20File#page=3'
        self.assertEqual(PDF.normalize_url(url),url.split('#')[0])
        for url in ('file:///etc/passwd','https://user:secret@example.com/report.pdf'):
            with self.assertRaises(ValueError):
                PDF.normalize_url(url)

    def test_cli_non_success_returns_json_and_nonzero(self):
        result=subprocess.run([sys.executable,str(SCRIPT),self.url+'/html.pdf','--output-dir',str(self.root)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)['status'],'not_pdf')


if __name__=='__main__':
    unittest.main()
