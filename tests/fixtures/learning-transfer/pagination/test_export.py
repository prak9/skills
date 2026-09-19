import unittest

from exporter import export_rows


class ExportTests(unittest.TestCase):
    def test_success_status(self):
        self.assertEqual(200, export_rows()["status"])


if __name__ == "__main__":
    unittest.main()
