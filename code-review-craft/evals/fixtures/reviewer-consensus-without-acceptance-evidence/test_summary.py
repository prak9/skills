import unittest

from summary import summarize


class SummaryTests(unittest.TestCase):
    def test_integer_cents(self):
        orders = [{"id": "a", "amount_cents": 101}, {"id": "b", "amount_cents": 202}]
        self.assertEqual({"count": 2, "total_cents": 303}, summarize(orders))

    def test_empty_batch(self):
        self.assertEqual({"count": 0, "total_cents": 0}, summarize([]))


if __name__ == "__main__":
    unittest.main()
