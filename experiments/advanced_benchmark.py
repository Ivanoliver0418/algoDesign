"""
Ivan Oliver
cpf150
11383104
CMPT360
"""

"""
CMPT 360 - Option 4: Cover
Advanced Experimental Evaluation

Compare three exact algorithms:
1. Baseline exhaustive search
2. Original cactus-subset enumeration
3. Optimized cactus-subset enumeration

We test:
- Unavoidable cacti
- Optional cacti
- Randomly generated instances

Results are saved to results/advanced_benchmark.csv.
"""

import csv
import random
import sys
from itertools import combinations
from pathlib import Path
from statistics import median
from time import perf_counter


# Find the main project directory.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from baseline import solve_cover as solve_baseline
from fasterAlgo import solve_cover as solve_optimized


# Number of timing runs for each algorithm.
REPEATS = 3


def solve_plain(O, C, S, R):
    """
    Original cactus-subset algorithm before pruning.

    We keep this version here to measure whether
    our new optimizations actually improve performance.
    """

    if not O:
        return [], 0

    orange_masks = []
    cactus_masks = []

    # Precompute the orange and cactus coverage
    # of every sprinkler using bitmasks.
    for position, radius in zip(S, R):

        left = position - radius
        right = position + radius

        orange_mask = 0
        cactus_mask = 0

        for j, orange in enumerate(O):
            if left <= orange <= right:
                orange_mask |= 1 << j

        for j, cactus in enumerate(C):
            if left <= cactus <= right:
                cactus_mask |= 1 << j

        orange_masks.append(orange_mask)
        cactus_masks.append(cactus_mask)

    all_oranges = (1 << len(O)) - 1

    # Try every allowed cactus subset, starting
    # with the subsets containing the fewest cacti.
    for budget in range(len(C) + 1):

        for cactus_subset in combinations(
            range(len(C)), budget
        ):

            allowed = 0

            for j in cactus_subset:
                allowed |= 1 << j

            selected = []
            covered = 0
            watered = 0

            for i in range(len(S)):

                # Reject sprinklers that water
                # a cactus outside our allowed set.
                if cactus_masks[i] & ~allowed:
                    continue

                # Skip sprinklers that add no new oranges.
                if (orange_masks[i] | covered) == covered:
                    continue

                selected.append(i)
                covered |= orange_masks[i]
                watered |= cactus_masks[i]

                # Return once every orange is covered.
                if covered == all_oranges:
                    cost = bin(watered).count("1")
                    return selected, cost

    return None


def make_unavoidable_case(c):
    """
    Create a case where every cactus must be watered.

    Orange trees are at positions 0 and 100.
    Sprinklers covering the first orange also
    water every cactus.

    Our optimized algorithm should identify
    all the cacti as unavoidable.
    """

    O = [0, 100]
    C = list(range(1, c + 1))

    # Alternate between sprinklers that cover
    # the left orange and the right orange.
    S = [
        25 if i % 2 == 0 else 75
        for i in range(8)
    ]

    R = [25] * len(S)

    return O, C, S, R


def make_optional_case(k):
    """
    Create a case where cacti are optional.

    Each orange has two possible sprinklers:
    - One waters the cactus on its left.
    - One waters the cactus on its right.

    Neither cactus is individually unavoidable,
    but we must water at least one per orange.

    This gives k oranges and 2*k optional cacti.
    """

    O = []
    C = []
    S = []
    R = []

    for i in range(k):

        # Space orange groups far apart so their
        # sprinklers cannot cover other groups.
        center = i * 100

        O.append(center)

        # Place one cactus on each side.
        C.extend([
            center - 2,
            center + 2
        ])

        # Two sprinkler choices for this orange.
        S.extend([
            center - 1,
            center + 1
        ])

        R.extend([1, 1])

    return O, C, S, R


def make_random_case(rng, s):
    """
    Generate a reproducible random instance.

    We place a sprinkler at each orange's position
    to guarantee that a valid solution exists.
    The remaining sprinklers are randomly placed.
    """

    # Generate three distinct orange positions.
    O = rng.sample(range(61), 3)

    # Keep cactus positions separate from oranges.
    possible_cacti = [
        p for p in range(61)
        if p not in O
    ]

    C = rng.sample(possible_cacti, 6)

    # Include one sprinkler for every orange.
    S = O[:] + [
        rng.randint(0, 60)
        for _ in range(s - len(O))
    ]

    # Assign random radii.
    R = [
        rng.randint(0, 8)
        for _ in range(s)
    ]

    return O, C, S, R


def verify(case, result):
    """
    Confirm that an algorithm's solution is valid.

    Check:
    - Sprinkler indices are valid.
    - Every orange is watered.
    - The reported cactus count is correct.
    """

    O, C, S, R = case

    # All generated instances should be feasible.
    if result is None:
        raise AssertionError("Expected a valid solution")

    selected, cost = result

    # A sprinkler should not appear twice.
    if len(selected) != len(set(selected)):
        raise AssertionError("Duplicate sprinkler index")

    # Check that every selected index exists.
    if any(i < 0 or i >= len(S) for i in selected):
        raise AssertionError("Invalid sprinkler index")

    # Determine whether a position receives water.
    def is_watered(point):
        return any(
            S[i] - R[i] <= point <= S[i] + R[i]
            for i in selected
        )

    # Verify that every orange is watered.
    if not all(is_watered(p) for p in O):
        raise AssertionError("An orange is not watered")

    # Independently calculate the cactus count.
    actual_cost = sum(
        is_watered(p) for p in C
    )

    if cost != actual_cost:
        raise AssertionError("Incorrect cactus count")

    return cost


def measure(solver, case):
    """
    Measure an algorithm's running time.

    Use the median of three runs to reduce the
    effect of occasional timing fluctuations.

    Validation is performed outside the timer.
    """

    # Warm up the solver before measuring.
    verify(case, solver(*case))

    times = []
    costs = []

    for _ in range(REPEATS):

        # Start timing.
        start = perf_counter()

        result = solver(*case)

        # Convert seconds into milliseconds.
        elapsed = (perf_counter() - start) * 1000

        times.append(elapsed)

        # Verify the answer after timing.
        costs.append(verify(case, result))

    # Repeated runs should give the same optimal cost.
    if len(set(costs)) != 1:
        raise AssertionError("Inconsistent results")

    return median(times), costs[0]


def main():

    # Fixed seed makes random experiments reproducible.
    rng = random.Random(360)

    cases = []

    # Experiment 1:
    # Increase the number of unavoidable cacti.
    for c in [2, 4, 8, 12]:
        cases.append((
            "unavoidable",
            f"c={c}",
            make_unavoidable_case(c)
        ))

    # Experiment 2:
    # Increase the number of optional cacti.
    for k in [2, 3, 4, 5, 6]:
        cases.append((
            "optional",
            f"k={k}",
            make_optional_case(k)
        ))

    # Experiment 3:
    # Generate three random inputs for each
    # sprinkler count.
    for s in [4, 8, 12]:
        for trial in range(1, 4):
            cases.append((
                "random",
                f"s={s},trial={trial}",
                make_random_case(rng, s)
            ))

    results = []

    print(
        f"{'Scenario':<13} {'Instance':<14} "
        f"{'s':>2} {'c':>2} {'Cost':>4} "
        f"{'Baseline ms':>12} {'Plain ms':>10} "
        f"{'Optimized ms':>13}"
    )

    print("-" * 81)

    # Run all three algorithms on the same inputs.
    for scenario, instance, case in cases:

        O, C, S, R = case

        baseline_ms, baseline_cost = measure(
            solve_baseline, case
        )

        plain_ms, plain_cost = measure(
            solve_plain, case
        )

        optimized_ms, optimized_cost = measure(
            solve_optimized, case
        )

        # All three exact algorithms must agree.
        if len({
            baseline_cost,
            plain_cost,
            optimized_cost
        }) != 1:
            raise AssertionError(
                f"Algorithms disagree: {scenario} {instance}"
            )

        # Save the measurements for later analysis.
        results.append({
            "scenario": scenario,
            "instance": instance,
            "sprinklers": len(S),
            "oranges": len(O),
            "cacti": len(C),
            "optimal_cost": baseline_cost,
            "baseline_ms": f"{baseline_ms:.6f}",
            "plain_ms": f"{plain_ms:.6f}",
            "optimized_ms": f"{optimized_ms:.6f}"
        })

        # Display the results in the terminal.
        print(
            f"{scenario:<13} {instance:<14} "
            f"{len(S):>2} {len(C):>2} "
            f"{baseline_cost:>4} "
            f"{baseline_ms:>12.3f} "
            f"{plain_ms:>10.3f} "
            f"{optimized_ms:>13.3f}"
        )

    # Save everything in a CSV file.
    output = ROOT / "results" / "advanced_benchmark.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0])
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved: {output}")


if __name__ == "__main__":
    main()