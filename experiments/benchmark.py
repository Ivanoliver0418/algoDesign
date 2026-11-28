"""
Ivan Oliver
cpf150
11383104
CMPT360
"""

"""
Option 4: Cover
Experimental Evaluation

Compare the running times of the baseline and faster
algorithms as the number of sprinklers and cacti changes.

Results are saved to results/benchmark.csv.
"""

import csv
import sys
from pathlib import Path
from statistics import median
from time import perf_counter


# Find the main project folder so we can import both algorithms.
ROOT = Path(__file__).resolve().parents[1]

# Run each algorithm three times and use the median time.
REPEATS = 3


def make_case(s, c):
    """
    Generate a controlled test case with:
    s = number of sprinklers
    c = number of cacti

    Two oranges are placed at 0 and 100.

    Left sprinklers water the first orange and all cacti.
    Right sprinklers water the second orange.

    This makes the optimal number of watered cacti equal
    to c, allowing us to study difficult cactus budgets.
    """

    if s < 2 or not 0 <= c <= 25:
        raise ValueError(
            "Require at least 2 sprinklers and 0 <= c <= 25"
        )

    O = [0, 100]

    # Place all cacti inside the left watering interval.
    C = [2 * i + 1 for i in range(c)]

    # Alternate between left and right sprinklers.
    S = [
        25 if i % 2 == 0 else 75
        for i in range(s)
    ]

    # All sprinklers have radius 25.
    R = [25] * s

    return O, C, S, R


def verify(case, result):
    """
    Check whether an algorithm returns a valid solution
    and whether its reported cactus cost is correct.
    """

    O, C, S, R = case

    # Our generated inputs are guaranteed to be feasible.
    if result is None:
        raise AssertionError("Expected a valid solution")

    selected, reported_cost = result

    # Check for duplicate or invalid sprinkler indices.
    if len(set(selected)) != len(selected):
        raise AssertionError("Duplicate sprinkler selected")

    if any(i < 0 or i >= len(S) for i in selected):
        raise AssertionError("Invalid sprinkler index")

    # Check whether a position is watered by any
    # sprinkler in the selected subset.
    def watered(position):
        return any(
            S[i] - R[i] <= position <= S[i] + R[i]
            for i in selected
        )

    # Every orange tree must receive water.
    if not all(watered(orange) for orange in O):
        raise AssertionError("An orange tree was left dry")

    # Count the actual number of watered cacti.
    actual_cost = sum(
        watered(cactus) for cactus in C
    )

    if actual_cost != reported_cost:
        raise AssertionError("Incorrect cactus cost")

    return reported_cost


def measure(solver, case):
    """
    Execute an algorithm multiple times and return
    its median running time in milliseconds.
    """

    timings = []
    cost = None

    for _ in range(REPEATS):

        # Start the timer immediately before the algorithm.
        start = perf_counter()

        result = solver(*case)

        # Stop timing when the algorithm finishes.
        elapsed = (perf_counter() - start) * 1000

        timings.append(elapsed)

        # Verify outside the timed section so validation
        # does not affect the algorithm's measured time.
        cost = verify(case, result)

    return median(timings), cost


def run_benchmarks(solve_baseline, solve_faster):
    """
    Run two experiments:
    1. Increase sprinklers while keeping cacti fixed.
    2. Increase cacti while keeping sprinklers fixed.
    """

    # Experiment 1:
    # Increase sprinklers while keeping cacti fixed at 3.
    cases = [
        ("vary_sprinklers", s, 3)
        for s in [2, 4, 6, 8, 10, 12, 14, 16]
    ]

    # Experiment 2:
    # Increase cacti while keeping sprinklers fixed at 8.
    cases += [
        ("vary_cacti", 8, c)
        for c in [0, 3, 6, 9, 12, 15]
    ]

    results = []

    print(
        f"{'Experiment':<17} {'s':>3} {'c':>3} "
        f"{'Optimal':>7} {'Baseline ms':>13} "
        f"{'Faster ms':>11}"
    )
    print("-" * 62)

    for experiment, s, c in cases:

        # Both algorithms receive the exact same input.
        case = make_case(s, c)

        # Measure baseline and faster algorithm separately.
        baseline_ms, baseline_cost = measure(
            solve_baseline, case
        )

        faster_ms, faster_cost = measure(
            solve_faster, case
        )

        # Exact algorithms must agree on the optimal cost.
        if baseline_cost != faster_cost:
            raise AssertionError(
                f"Algorithms disagree for s={s}, c={c}"
            )

        # Store results for our performance graphs.
        results.append({
            "experiment": experiment,
            "sprinklers": s,
            "oranges": len(case[0]),
            "cacti": c,
            "optimal_cacti_watered": baseline_cost,
            "baseline_ms": f"{baseline_ms:.6f}",
            "faster_ms": f"{faster_ms:.6f}"
        })

        # Print results in a readable table.
        print(
            f"{experiment:<17} {s:>3} {c:>3} "
            f"{baseline_cost:>7} "
            f"{baseline_ms:>13.3f} "
            f"{faster_ms:>11.3f}"
        )

    # Create results folder if it does not exist.
    output = ROOT / "results" / "benchmark.csv"
    output.parent.mkdir(parents=True, exist_ok=True)

    # Save the measurements into a CSV file.
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved results to {output}")


if __name__ == "__main__":

    # Import the two algorithms from our main project.
    sys.path.insert(0, str(ROOT))

    from baseline import solve_cover as solve_baseline
    from fasterAlgo import solve_cover as solve_faster

    run_benchmarks(solve_baseline, solve_faster)
