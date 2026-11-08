# Ivan Oliver
# cpf150
# 11383104
# CMPT332

"""
CMPT 360 - Option 4: Cover
Faster Algorithm: Cactus Subset Enumeration

Goal:
Water every orange tree while minimizing the number
of distinct cacti watered.

Main idea:
Instead of trying all subsets of sprinklers, try all
subsets of cacti that we are willing to water.

For each allowed cactus subset, select sprinklers that
avoid the forbidden cacti and cover all orange trees.

This approach works best when there are fewer cacti
than sprinklers.
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

    # Each sprinkler must have a corresponding radius.
    if len(S) != len(R):
        raise ValueError("S and R must have the same length")

    # Sprinkler radii cannot be negative.
    if any(radius < 0 for radius in R):
        raise ValueError("Sprinkler radii cannot be negative")

    # No sprinklers are needed if there are no oranges.
    if not O:
        return [], 0

    # Precompute which oranges and cacti each sprinkler
    # waters. We represent these sets using bitmasks.
    orange_masks = []
    cactus_masks = []

    for position, radius in zip(S, R):

        # Calculate the sprinkler's watering interval.
        left = position - radius
        right = position + radius

        oranges = 0
        cacti = 0

        # Set bit j to 1 if orange j is watered.
        for j, orange in enumerate(O):
            if left <= orange <= right:
                oranges |= 1 << j

        # Set bit j to 1 if cactus j is watered.
        for j, cactus in enumerate(C):
            if left <= cactus <= right:
                cacti |= 1 << j

        # Save the coverage masks for this sprinkler.
        orange_masks.append(oranges)
        cactus_masks.append(cacti)

    # A mask containing 1 for every orange tree.
    # Example: 3 oranges -> binary 111.
    all_oranges = (1 << len(O)) - 1

    # Try allowing 0 cacti to get wet, then 1,
    # then 2, until we find a valid solution.
    for budget in range(len(C) + 1):

        # Generate all cactus subsets of this size.
        for cactus_subset in combinations(
            range(len(C)), budget
        ):

            # Create a mask of cacti allowed to get wet.
            allowed_cacti = 0

            for j in cactus_subset:
                allowed_cacti |= 1 << j

            # Track the current sprinkler selection.
            selected = []
            covered_oranges = 0
            actually_watered_cacti = 0

            # Examine every sprinkler.
            for i in range(len(S)):

                # Skip this sprinkler if it waters a
                # cactus outside the allowed subset.
                #
                # & checks for overlap between sets.
                # ~ identifies the forbidden cactus bits.
                if cactus_masks[i] & ~allowed_cacti:
                    continue

                # Skip this sprinkler if it does not
                # cover any new orange trees.
                #
                # | combines the already covered oranges
                # with the sprinkler's orange coverage.
                if (orange_masks[i] | covered_oranges) == covered_oranges:
                    continue

                # Select this sprinkler.
                selected.append(i)

                # Update the covered oranges and
                # the cacti that actually get wet.
                covered_oranges |= orange_masks[i]
                actually_watered_cacti |= cactus_masks[i]

                # Check whether every orange is covered.
                if covered_oranges == all_oranges:

                    # Count the number of distinct cacti
                    # watered by the selected sprinklers.
                    cost = bin(actually_watered_cacti).count("1")

                    # Since we try smaller cactus budgets
                    # first, this solution is optimal.
                    return selected, cost

    # No combination of sprinklers can cover all oranges.
    return None


def main():
    # Read the input JSON filename from the terminal.
    parser = argparse.ArgumentParser(
        description="Faster exact algorithm for CMPT 360 Cover"
    )
    parser.add_argument(
        "input_file",
        help="Path to an input JSON file"
    )
    args = parser.parse_args()

    # Load the orange, cactus, and sprinkler information.
    with open(args.input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Execute the faster algorithm.
    result = solve_cover(
        data["O"],
        data["C"],
        data["S"],
        data["R"]
    )

    # Handle cases where no valid solution exists.
    if result is None:
        print("No valid selection covers all orange trees.")
        return

    # Display the selected sprinklers and minimum cost.
    selected_indices, cost = result

    print("Selected indices (0-based):", selected_indices)
    print(
        "Selected sprinkler positions:",
        [data["S"][i] for i in selected_indices]
    )
    print("Number of cacti watered:", cost)


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()