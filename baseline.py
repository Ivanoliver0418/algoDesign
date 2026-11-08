
# Ivan Oliver
# cpf150
# 11383104
# CMPT332

"""
CMPT 360 - Option 4: Cover
Baseline Algorithm: Exhaustive Search

Goal:
Select sprinklers that water every orange tree while
minimizing the number of distinct cacti watered.

Each sprinkler i covers the interval:
[S[i] - R[i], S[i] + R[i]]
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

    # A sprinkler cannot have a negative radius.
    if any(radius < 0 for radius in R):
        raise ValueError("Sprinkler radii cannot be negative")

    # Store the best solution found so far.
    best_selection = None
    best_cost = float("inf")

    # Try every possible subset of sprinklers.
    # With s sprinklers, there are 2^s subsets.
    for size in range(len(S) + 1):
        for subset in combinations(range(len(S)), size):

            # Initially, no orange trees or cacti are watered.
            covered_oranges = [False] * len(O)
            watered_cacti = [False] * len(C)

            # Check the coverage of each selected sprinkler.
            for i in subset:

                # Calculate the sprinkler's watering interval.
                left = S[i] - R[i]
                right = S[i] + R[i]

                # Check which orange trees are watered.
                for j, orange in enumerate(O):
                    if left <= orange <= right:
                        covered_oranges[j] = True

                # Check which cacti are watered.
                for j, cactus in enumerate(C):
                    if left <= cactus <= right:
                        watered_cacti[j] = True

            # Reject this subset if an orange tree is dry.
            if not all(covered_oranges):
                continue

            # Count distinct cacti watered.
            # Using Booleans prevents double counting.
            cost = sum(watered_cacti)

            # Update the best solution if this one is better.
            if cost < best_cost:
                best_selection = list(subset)
                best_cost = cost

    # No subset was able to water every orange tree.
    if best_selection is None:
        return None

    return best_selection, best_cost


def main():
    # Read the input JSON filename from the terminal.
    parser = argparse.ArgumentParser(
        description="Exact baseline for CMPT 360 Cover"
    )
    parser.add_argument(
        "input_file",
        help="Path to an input JSON file"
    )
    args = parser.parse_args()

    # Load the positions and radii from the JSON file.
    with open(args.input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Execute the baseline algorithm.
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

    # Display the selected sprinklers and the minimum cost.
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