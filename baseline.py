
# Ivan Oliver
# cpf150
# 11383104
# CMPT332

from itertools import combinations

def solve_cover(O, C, S, R):
    if len(S) != len(R):
        raise ValueError("S and R must have the same length")

    if any(radius < 0 for radius in R):
        raise ValueError("Sprinkler radii cannot be negative")

    best_selection = None
    best_cost = float("inf")

    for size in range(len(S) + 1):
        for subset in combinations(range(len(S)), size):
            covered_oranges = [False] * len(O)
            watered_cacti = [False] * len(C)

            for i in subset:
                left = S[i] - R[i]
                right = S[i] + R[i]

                for j, orange in enumerate(O):
                    if left <= orange <= right:
                        covered_oranges[j] = True

                for j, cactus in enumerate(C):
                    if left <= cactus <= right:
                        watered_cacti[j] = True

            if not all(covered_oranges):
                continue

            cost = sum(watered_cacti)

            if cost < best_cost:
                best_selection = list(subset)
                best_cost = cost

    if best_selection is None:
        return None

    return best_selection, best_cost
