import unittest

from catalog import render_catalog


class CatalogTests(unittest.TestCase):
    def test_two_items(self):
        self.assertEqual(
            {"count": 2, "names": ["Desk", "Lamp"]},
            render_catalog([{"name": "Desk"}, {"name": "Lamp"}]),
        )

    def test_empty_catalog(self):
        self.assertEqual({"count": 0, "names": []}, render_catalog([]))


if __name__ == "__main__":
    unittest.main()
