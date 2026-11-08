# Ivan Oliver
# cpf150
# 11383104
# CMPT332

"""
CMPT 360 - Option 4: Cover
Unit Tests for the Baseline Algorithm

These tests verify that exhaustive search:
1. Finds an optimal sprinkler selection.
2. Covers all orange trees.
3. Counts each watered cactus only once.
4. Handles edge cases and invalid inputs.
"""

import unittest

from baseline import solve_cover


class TestBaseline(unittest.TestCase):

    def test_optimization_example(self):
        # Using two sprinklers is better than using
        # one wide sprinkler that waters a cactus.
        O = [2, 6]
        C = [4]
        S = [2, 6, 4]
        R = [0, 0, 2]

        result = solve_cover(O, C, S, R)

        # Sprinklers 0 and 1 cover both oranges
        # without watering any cacti.
        self.assertEqual(result, ([0, 1], 0))

    def test_no_valid_solution(self):
        # The only sprinkler cannot reach the orange.
        O = [5]
        C = []
        S = [0]
        R = [1]

        result = solve_cover(O, C, S, R)

        # No valid sprinkler subset exists.
        self.assertIsNone(result)

    def test_interval_boundaries(self):
        # A sprinkler at position 4 with radius 2
        # covers the inclusive interval [2, 6].
        O = [2, 6]
        C = []
        S = [4]
        R = [2]

        result = solve_cover(O, C, S, R)

        # Both oranges are exactly on the boundaries.
        self.assertEqual(result, ([0], 0))

    def test_overlapping_sprinklers(self):
        # Both sprinklers water the cactus at position 4.
        # The cactus should only be counted once.
        O = [1, 7]
        C = [4]
        S = [2, 6]
        R = [2, 2]

        result = solve_cover(O, C, S, R)

        self.assertEqual(result, ([0, 1], 1))

    def test_no_orange_trees(self):
        # If there are no oranges, we do not need
        # to turn on any sprinklers.
        O = []
        C = [2, 4]
        S = [2, 4]
        R = [1, 1]

        result = solve_cover(O, C, S, R)

        self.assertEqual(result, ([], 0))

    def test_no_sprinklers(self):
        # An orange exists, but no sprinklers are available.
        O = [3]
        C = [5]
        S = []
        R = []

        result = solve_cover(O, C, S, R)

        self.assertIsNone(result)

    def test_mismatched_arrays(self):
        # Each sprinkler must have exactly one radius.
        O = [2]
        C = []
        S = [2, 4]
        R = [1]

        # The algorithm should reject invalid input.
        with self.assertRaises(ValueError):
            solve_cover(O, C, S, R)

    def test_negative_radius(self):
        # A negative watering radius is invalid.
        O = [2]
        C = []
        S = [2]
        R = [-1]

        with self.assertRaises(ValueError):
            solve_cover(O, C, S, R)


# Run tests if this file is executed directly.
if __name__ == "__main__":
    unittest.main()