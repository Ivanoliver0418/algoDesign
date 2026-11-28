"""
Ivan Oliver
cpf150
11383104
CMPT360
"""

"""
CMPT 360 - Option 4: Cover
Advanced Benchmark Graphs

Generate three performance graphs:
1. Unavoidable cacti
2. Optional cacti
3. Random instances

The graphs compare:
- Baseline exhaustive search
- Original cactus-subset algorithm
- Optimized cactus-subset algorithm
"""

import csv
from pathlib import Path
from statistics import median

import matplotlib.pyplot as plt


# Find the main project directory.
ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "results" / "advanced_benchmark.csv"
OUTPUT_DIR = ROOT / "results"


def load_results():
    """
    Read the advanced benchmark results from CSV.
    Convert numerical values into Python numbers.
    """

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Run advanced_benchmark.py first."
        )

    results = []

    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            results.append({
                "scenario": row["scenario"],
                "sprinklers": int(row["sprinklers"]),
                "cacti": int(row["cacti"]),
                "baseline_ms": float(row["baseline_ms"]),
                "plain_ms": float(row["plain_ms"]),
                "optimized_ms": float(row["optimized_ms"])
            })

    return results


def plot_scenario(
    results, scenario, x_column, x_label, title, filename
):
    """
    Generate one graph for a selected scenario.

    If multiple trials have the same x-axis value,
    use the median running time.
    """

    # Keep only measurements for this scenario.
    data = [
        row for row in results
        if row["scenario"] == scenario
    ]

    if not data:
        raise ValueError(
            f"No data found for scenario: {scenario}"
        )

    # Group rows that have the same x-axis value.
    grouped = {}

    for row in data:
        x = row[x_column]

        if x not in grouped:
            grouped[x] = []

        grouped[x].append(row)

    # Sort x-axis values in increasing order.
    x_values = sorted(grouped)

    algorithms = [
        ("baseline_ms", "Baseline", "o"),
        ("plain_ms", "Original cactus subsets", "s"),
        ("optimized_ms", "Optimized cactus subsets", "^")
    ]

    # Create a separate graph for this scenario.
    fig, ax = plt.subplots(figsize=(9, 5))

    for column, label, marker in algorithms:

        # Use median time when multiple trials exist.
        times = [
            median(row[column] for row in grouped[x])
            for x in x_values
        ]

        if any(time <= 0 for time in times):
            raise ValueError(
                "Running times must be positive."
            )

        ax.plot(
            x_values,
            times,
            marker=marker,
            linewidth=2,
            label=label
        )

    # Add graph title and labels.
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Running Time (milliseconds)")

    # Log scale makes large runtime differences
    # easier to compare on the same graph.
    ax.set_yscale("log")

    # Display the exact tested x-axis values.
    ax.set_xticks(x_values)

    ax.grid(
        True,
        which="both",
        linestyle="--",
        alpha=0.4
    )

    ax.legend()

    # Prevent graph labels from being cut off.
    fig.tight_layout()

    # Save the graph at high resolution.
    output = OUTPUT_DIR / filename

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved: {output}")


def main():

    # Read the actual experimental measurements.
    results = load_results()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Experiment 1:
    # Increasing the number of unavoidable cacti.
    plot_scenario(
        results,
        scenario="unavoidable",
        x_column="cacti",
        x_label="Number of Unavoidable Cacti",
        title="Performance with Unavoidable Cacti",
        filename="advanced_unavoidable.png"
    )

    # Experiment 2:
    # Increasing the number of optional cacti.
    plot_scenario(
        results,
        scenario="optional",
        x_column="cacti",
        x_label="Number of Optional Cacti",
        title="Performance with Optional Cacti",
        filename="advanced_optional.png"
    )

    # Experiment 3:
    # Increasing sprinklers in random instances.
    # Each point is the median of three trials.
    plot_scenario(
        results,
        scenario="random",
        x_column="sprinklers",
        x_label="Number of Sprinklers",
        title="Performance on Random Instances",
        filename="advanced_random.png"
    )

    print("\nAll advanced graphs generated.")


if __name__ == "__main__":
    main()