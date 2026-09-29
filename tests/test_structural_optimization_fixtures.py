"""Check arithmetic counterexamples, not an agent's use of skill instructions."""

from fractions import Fraction
import unittest


class StructuralOptimizationFixtureTests(unittest.TestCase):
    def test_monotone_penalty_counts_can_skip_target(self):
        costs = {1: 10, 2: 9, 3: 0}
        # For count 2 to beat both neighbors, lambda must lie in this interval.
        lower = Fraction(costs[2] - costs[3], 3 - 2)
        upper = Fraction(costs[1] - costs[2], 2 - 1)
        self.assertGreater(lower, upper)
        counts = [min(costs, key=lambda m: (costs[m] + penalty * m, m))
                  for penalty in range(11)]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertNotIn(2, counts)
        relaxed = min(cost + 5 * count for count, cost in costs.items()) - 5 * 2
        self.assertEqual(5, relaxed)
        self.assertLess(relaxed, costs[2])

    def test_present_winner_can_lose_after_update(self):
        a = lambda t: t
        b = lambda t: 2 * t - 3
        self.assertLess(b(0), a(0))
        self.assertLess(a(4), b(4))
        exact = [min(a(t), b(t)) for t in range(11)]
        pruned = [b(t) for t in range(11)]
        self.assertNotEqual(exact, pruned)

    def test_equal_current_cost_can_hide_different_completions(self):
        edges = {"B": [("C", 1), ("A", 100)], "C": [("Z", 1)],
                 "A": [("Z", 1)]}

        def complete(vertex, visited, cost):
            if vertex == "Z":
                return [cost] if {"A", "B", "C"} <= visited else []
            return [result for neighbor, weight in edges[vertex]
                    for result in complete(neighbor, visited | {neighbor}, cost + weight)]

        self.assertEqual([7], complete("B", {"A", "B"}, 5))
        self.assertEqual([106], complete("B", {"B", "C"}, 5))

    def test_interval_mapping_preserves_witness_and_allows_idle(self):
        duration = 3
        starts = [(a, b) for a in range(11) for b in [2]]
        original = {(a, b) for a, b in starts if abs(a - b) >= duration}
        nonoverlap = lambda a, b: a + duration <= b or b + duration <= a
        corrected = {(a, b) for a, b in starts
                     if a + duration <= 10 + duration
                     and b + duration <= 2 + duration and nonoverlap(a, b)}
        wrong_deadlines = {(a, b) for a, b in starts
                           if a + duration <= 10 and b + duration <= 2
                           and nonoverlap(a, b)}
        self.assertEqual(original, corrected)
        self.assertIn((5, 2), original)
        self.assertFalse(wrong_deadlines)
        self.assertFalse(any(a == 0 for a, b in original))


if __name__ == "__main__":
    unittest.main()
