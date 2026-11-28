"""
Ivan Oliver
cpf150
11383104
CMPT360
"""

"""
CMPT 360 - Option 4: Cover
Scalability and Memory Evaluation

Compare the baseline and optimized algorithms
on increasingly difficult problems.

Each algorithm runs in a separate process so
we can stop experiments that take too long.
"""

import csv
import json
import platform
import subprocess
import sys
import tracemalloc
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()

# Maximum solver running time in seconds.
TIME_LIMIT = 2.0


def make_case(family, n):
    """Generate two types of test instances."""

    if family == "many_sprinklers":
        # Keep 3 unavoidable cacti while
        # increasing the number of sprinklers.
        O = [0, 100]
        C = [1, 3, 5]

        S = [
            25 if i % 2 == 0 else 75
            for i in range(n)
        ]

        R = [25] * n

    elif family == "optional_cacti":
        # Each orange has two sprinkler choices.
        # Each choice waters a different cactus.
        O, C, S, R = [], [], [], []

        for i in range(n):
            center = i * 100

            O.append(center)
            C.extend([center - 2, center + 2])
            S.extend([center - 1, center + 1])
            R.extend([1, 1])

    else:
        raise ValueError("Unknown case family")

    return O, C, S, R


def verify(case, answer):
    """Check orange coverage and cactus cost."""

    if answer is None:
        raise AssertionError(
            "Generated case should be solvable"
        )

    O, C, S, R = case
    chosen, cost = answer

    # Make sure the selected indices are valid.
    if len(set(chosen)) != len(chosen):
        raise AssertionError("Duplicate sprinkler")

    if any(i < 0 or i >= len(S) for i in chosen):
        raise AssertionError("Invalid sprinkler index")

    # Check whether a position receives water.
    def watered(position):
        return any(
            S[i] - R[i] <= position <= S[i] + R[i]
            for i in chosen
        )

    # Every orange must be watered.
    if not all(watered(orange) for orange in O):
        raise AssertionError("An orange was left dry")

    # Verify the reported cactus count.
    actual_cost = sum(
        watered(cactus) for cactus in C
    )

    if cost != actual_cost:
        raise AssertionError("Incorrect cactus cost")

    return cost


def worker(family, n, algorithm):
    """
    Run one algorithm in a separate process.

    Measure its running time and peak traced
    Python memory allocations.
    """

    sys.path.insert(0, str(ROOT))

    if algorithm == "baseline":
        from baseline import solve_cover
    else:
        from fasterAlgo import solve_cover

    case = make_case(family, n)

    # Start measuring Python memory allocations.
    tracemalloc.start()

    # Measure the algorithm's running time.
    start = perf_counter()
    answer = solve_cover(*case)
    seconds = perf_counter() - start

    # Record the peak traced memory.
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Verify the solution after timing.
    cost = verify(case, answer)

    print(json.dumps({
        "seconds": seconds,
        "peak_python_mib": peak_bytes / (1024 * 1024),
        "cost": cost
    }))


def run_case(family, n, algorithm):
    """
    Execute a solver with a safety timeout.

    If it takes too long, stop the process
    instead of letting it run indefinitely.
    """

    command = [
        sys.executable,
        str(SCRIPT),
        "--worker",
        family,
        str(n),
        algorithm
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            timeout=TIME_LIMIT + 2.0
        )

    except subprocess.TimeoutExpired:
        return "TIMEOUT", "", "", ""

    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            error.stderr.strip()
        ) from error

    result = json.loads(completed.stdout)

    # Check the solver time against our limit.
    status = (
        "OK"
        if result["seconds"] <= TIME_LIMIT
        else "OVER_LIMIT"
    )

    return (
        status,
        f'{result["seconds"]:.6f}',
        f'{result["peak_python_mib"]:.6f}',
        result["cost"]
    )


def main():
    # Increase sprinklers while keeping cacti fixed.
    cases = [
        ("many_sprinklers", s)
        for s in [4, 8, 12, 14, 16, 18, 20]
    ]

    # Increase the number of optional cacti.
    cases += [
        ("optional_cacti", k)
        for k in [2, 3, 4, 5, 6, 7, 8]
    ]

    records = []

    print(
        f"Python {platform.python_version()} "
        f"on {platform.platform()}"
    )

    print(f"Solver time limit: {TIME_LIMIT} seconds")
    print(
        "Memory measures Python allocations, "
        "not total process RAM.\n"
    )

    for family, n in cases:
        O, C, S, R = make_case(family, n)

        # Run both algorithms on the same problem.
        for algorithm in ("baseline", "optimized"):

            status, seconds, memory, cost = run_case(
                family, n, algorithm
            )

            # Save the results for our report.
            records.append({
                "family": family,
                "size_parameter": n,
                "algorithm": algorithm,
                "sprinklers": len(S),
                "oranges": len(O),
                "cacti": len(C),
                "status": status,
                "time_s": seconds,
                "peak_python_mib": memory,
                "cost": cost
            })

            print(
                f"{family:17} n={n:<2} "
                f"{algorithm:10} {status:10} "
                f"{str(seconds):>10} s "
                f"{str(memory):>10} MiB"
            )

    # Save results to a CSV file.
    output = ROOT / "results" / "scalability.csv"
    output.parent.mkdir(exist_ok=True)

    with output.open(
        "w", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys()
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"\nSaved: {output}")


if __name__ == "__main__":

    # Child process: run a single algorithm.
    if len(sys.argv) == 5 and sys.argv[1] == "--worker":
        worker(
            sys.argv[2],
            int(sys.argv[3]),
            sys.argv[4]
        )

    # Normal execution: run all experiments.
    else:
        main()