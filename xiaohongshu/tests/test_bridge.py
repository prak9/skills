import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime' / 'scripts'))
import websockets
from websockets.exceptions import InvalidStatus
from bridge_server import ALLOWED_ORIGINS, BridgeServer


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bridge = BridgeServer()
        self.server = await websockets.serve(self.bridge.handle, '127.0.0.1', 0, origins=ALLOWED_ORIGINS)
        self.url = 'ws://127.0.0.1:' + str(self.server.sockets[0].getsockname()[1])

    async def asyncTearDown(self):
        self.server.close()
        await self.server.wait_closed()

    async def test_web_origin_rejected(self):
        with self.assertRaises(InvalidStatus) as rejected:
            async with websockets.connect(self.url, origin='https://example.com'):
                pass
        self.assertEqual(rejected.exception.response.status_code, 403)

    async def test_status_does_not_require_extension(self):
        async with websockets.connect(self.url) as client:
            await client.send(json.dumps({'role': 'cli', 'method': 'ping_server'}))
            self.assertFalse(json.loads(await client.recv())['result']['extension_connected'])

    async def test_extension_response_routed_and_pending_cleaned(self):
        async with websockets.connect(self.url, origin='chrome-extension://' + 'a' * 32) as extension:
            await extension.send(json.dumps({'role': 'extension'}))
            for _ in range(100):
                if self.bridge._extension_ws:
                    break
                await asyncio.sleep(.001)
            async with websockets.connect(self.url) as client:
                await client.send(json.dumps({'role': 'cli', 'method': 'get_element_text'}))
                request = json.loads(await asyncio.wait_for(extension.recv(), 2))
                await extension.send(json.dumps({'id': request['id'], 'result': 'fixture result'}))
                self.assertEqual(json.loads(await client.recv())['result'], 'fixture result')
                self.assertEqual(self.bridge._pending, {})


if __name__ == '__main__':
    unittest.main()
