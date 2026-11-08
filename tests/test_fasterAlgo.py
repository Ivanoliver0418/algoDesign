# Ivan Oliver
# cpf150
# 11383104
# CMPT332

"""
CMPT 360 - Option 4: Cover
Unit Tests for the Faster Algorithm

These tests verify that:
1. The faster algorithm finds optimal solutions.
2. Every orange tree is covered.
3. Each watered cactus is counted once.
4. Edge cases and invalid inputs are handled.
5. Results match the exact baseline algorithm.
"""

import random
import unittest

from baseline import solve_cover as solve_baseline
from fasterAlgo import solve_cover as solve_faster


class TestFasterAlgo(unittest.TestCase):

    def test_optimization_example(self):
        # Two narrow sprinklers avoid watering the cactus.
        O = [2, 6]
        C = [4]
        S = [2, 6, 4]
        R = [0, 0, 2]

        result = solve_faster(O, C, S, R)

        self.assertEqual(result, ([0, 1], 0))

    def test_no_valid_solution(self):
        # The sprinkler cannot reach the orange tree.
        O = [5]
        C = []
        S = [0]
        R = [1]

        self.assertIsNone(solve_faster(O, C, S, R))

    def test_interval_boundaries(self):
        # Sprinkler coverage includes both endpoints.
        O = [2, 6]
        C = []
        S = [4]
        R = [2]

        self.assertEqual(
            solve_faster(O, C, S, R),
            ([0], 0)
        )

    def test_overlapping_sprinklers(self):
        # Both sprinklers water the same cactus.
        # It should only be counted once.
        O = [1, 7]
        C = [4]
        S = [2, 6]
        R = [2, 2]

        self.assertEqual(
            solve_faster(O, C, S, R),
            ([0, 1], 1)
        )

    def test_no_orange_trees(self):
        # No oranges means no sprinklers are needed.
        O = []
        C = [2, 4]
        S = [2, 4]
        R = [1, 1]

        self.assertEqual(
            solve_faster(O, C, S, R),
            ([], 0)
        )

    def test_no_sprinklers(self):
        # An orange cannot be watered without sprinklers.
        O = [3]
        C = [5]
        S = []
        R = []

        self.assertIsNone(solve_faster(O, C, S, R))

    def test_mismatched_arrays(self):
        # Every sprinkler must have a radius.
        with self.assertRaises(ValueError):
            solve_faster([2], [], [2, 4], [1])

    def test_negative_radius(self):
        # Negative radii are invalid.
        with self.assertRaises(ValueError):
            solve_faster([2], [], [2], [-1])

    def test_random_against_baseline(self):
        # Use a fixed seed so tests are reproducible.
        rng = random.Random(360)

        # Generate 100 different small problems.
        for _ in range(100):

            # Randomly choose the number of objects.
            o = rng.randint(0, 5)
            c = rng.randint(0, 4)
            s = rng.randint(0, 6)

            # Generate random object positions.
            O = [rng.randint(0, 15) for _ in range(o)]
            C = [rng.randint(0, 15) for _ in range(c)]
            S = [rng.randint(0, 15) for _ in range(s)]

            # Give every sprinkler a random radius.
            R = [rng.randint(0, 6) for _ in range(s)]

            # Solve the same problem using both algorithms.
            baseline = solve_baseline(O, C, S, R)
            faster = solve_faster(O, C, S, R)

            # If no solution exists, both should return None.
            if baseline is None:
                self.assertIsNone(faster)
                continue

            # The faster algorithm must also find a solution.
            self.assertIsNotNone(faster)

            selected, cost = faster

            # Both algorithms must find the same optimal cost.
            # They may select different optimal sprinklers.
            self.assertEqual(cost, baseline[1])

            # Verify that the selected sprinklers cover
            # every orange tree.
            for orange in O:
                covered = any(
                    S[i] - R[i] <= orange <= S[i] + R[i]
                    for i in selected
                )
                self.assertTrue(covered)

            # Recalculate the actual number of cacti watered.
            actual_cost = sum(
                any(
                    S[i] - R[i] <= cactus <= S[i] + R[i]
                    for i in selected
                )
                for cactus in C
            )

            # Confirm that the reported cost is correct.
            self.assertEqual(cost, actual_cost)


if __name__ == "__main__":
    unittest.main()