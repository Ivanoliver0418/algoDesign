# Ivan Oliver
# cpf150
# 11383104
# CMPT332

"""
CMPT 360 - Option 4: Cover
Faster Algorithm: Optimized Cactus Subset Enumeration

Goal:
Water every orange tree while minimizing the number
of distinct cacti watered.

Main improvements:
1. Identify cacti that must be watered.
2. Ignore sprinklers that cover no orange trees.
3. Ignore cacti that are irrelevant to the solution.
4. Enumerate only the remaining optional cacti.

The algorithm still guarantees an optimal solution.
"""

import argparse
import json
from itertools import combinations


def solve_cover(O, C, S, R):
    """
    O: Positions of orange trees
    C: Positions of cacti
    S: Positions of sprinklers
    R: Radius of each sprinkler

    Returns:
        (selected sprinkler indices, minimum cacti watered)
        or None if no valid solution exists.
    """

    # Check that each sprinkler has a radius.
    if len(S) != len(R):
        raise ValueError("S and R must have the same length")

    if any(radius < 0 for radius in R):
        raise ValueError("Sprinkler radii cannot be negative")

    # No sprinklers are needed if there are no oranges.
    if not O:
        return [], 0

    orange_masks = []
    cactus_masks = []
    useful = []

    # Precompute the objects covered by each sprinkler.
    for i, (position, radius) in enumerate(zip(S, R)):
        left = position - radius
        right = position + radius

        oranges = 0
        cacti = 0

        # Set one bit for every orange watered.
        for j, orange in enumerate(O):
            if left <= orange <= right:
                oranges |= 1 << j

        # Set one bit for every cactus watered.
        for j, cactus in enumerate(C):
            if left <= cactus <= right:
                cacti |= 1 << j

        orange_masks.append(oranges)
        cactus_masks.append(cacti)

        # A sprinkler covering no oranges is unnecessary.
        if oranges != 0:
            useful.append(i)

    # Target mask: every orange tree must be covered.
    all_oranges = (1 << len(O)) - 1

    # --------------------------------------------------
    # Optimization 1: Find unavoidable cacti.
    # --------------------------------------------------

    forced_cacti = 0

    for j in range(len(O)):

        # Find sprinklers that can water orange j.
        covering = [
            i for i in useful
            if orange_masks[i] & (1 << j)
        ]

        # If no sprinkler reaches this orange,
        # the entire problem is impossible.
        if not covering:
            return None

        # Find cacti watered by EVERY sprinkler
        # capable of covering this orange.
        common_cacti = cactus_masks[covering[0]]

        for i in covering[1:]:
            common_cacti &= cactus_masks[i]

        # These cacti must be watered in any solution.
        forced_cacti |= common_cacti

    # --------------------------------------------------
    # Optimization 2: Remove irrelevant cacti.
    # --------------------------------------------------

    relevant_cacti = 0

    # Only consider cacti watered by sprinklers
    # that can cover at least one orange.
    for i in useful:
        relevant_cacti |= cactus_masks[i]

    # Keep only cacti that are relevant but not forced.
    # These are the cacti we actually need to enumerate.
    optional_indices = [
        j for j in range(len(C))
        if (relevant_cacti & (1 << j))
        and not (forced_cacti & (1 << j))
    ]

    # --------------------------------------------------
    # Optimization 3: Search optional cactus subsets.
    # --------------------------------------------------

    # Try allowing zero optional cacti, then one,
    # and continue until we find a valid solution.
    for budget in range(len(optional_indices) + 1):

        for cactus_subset in combinations(
            optional_indices, budget
        ):

            # Forced cacti are always allowed.
            allowed_cacti = forced_cacti

            # Add the optional cacti for this subset.
            for j in cactus_subset:
                allowed_cacti |= 1 << j

            selected = []
            covered_oranges = 0
            watered_cacti = 0

            # Examine only useful sprinklers.
            for i in useful:

                # Reject sprinklers watering forbidden cacti.
                if cactus_masks[i] & ~allowed_cacti:
                    continue

                # Skip sprinklers that add no new oranges.
                if (orange_masks[i] | covered_oranges) == covered_oranges:
                    continue

                # Select the sprinkler and update coverage.
                selected.append(i)
                covered_oranges |= orange_masks[i]
                watered_cacti |= cactus_masks[i]

                # All orange trees are now covered.
                if covered_oranges == all_oranges:

                    # Count distinct cacti actually watered.
                    cost = bin(watered_cacti).count("1")

                    # Smaller budgets were checked first,
                    # so this solution must be optimal.
                    return selected, cost

    # No valid sprinkler selection exists.
    return None


def main():
    # Read the JSON input filename.
    parser = argparse.ArgumentParser(
        description="Optimized exact algorithm for CMPT 360 Cover"
    )

    parser.add_argument(
        "input_file",
        help="Path to an input JSON file"
    )

    args = parser.parse_args()

    # Load the input data.
    with open(args.input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Run the optimized algorithm.
    result = solve_cover(
        data["O"],
        data["C"],
        data["S"],
        data["R"]
    )

    if result is None:
        print("No valid selection covers all orange trees.")
        return

    selected_indices, cost = result

    print("Selected indices (0-based):", selected_indices)
    print(
        "Selected sprinkler positions:",
        [data["S"][i] for i in selected_indices]
    )
    print("Number of cacti watered:", cost)


if __name__ == "__main__":
    main()