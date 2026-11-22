"""
Ivan Oliver
cpf150
11383104
CMPT332
"""

"""
CMPT 360 - Option 4: Cover
Experimental Evaluation - Performance Graphs

Goal:
Generate graphs comparing the running times of the
baseline and faster algorithms.

Input:
results/benchmark.csv

Output:
results/plot_vary_sprinklers.png
results/plot_vary_cacti.png
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# Find the main project directory.
ROOT = Path(__file__).resolve().parents[1]

# Location of the benchmark results.
INPUT_FILE = ROOT / "results" / "benchmark.csv"

# Directory where the graphs will be saved.
OUTPUT_DIR = ROOT / "results"


def load_results():
    """
    Read the benchmark CSV file and convert
    its numeric values into Python numbers.
    """

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "benchmark.csv not found. Run benchmark.py first."
        )

    results = []

    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Convert the CSV strings into numbers.
            results.append({
                "experiment": row["experiment"],
                "sprinklers": int(row["sprinklers"]),
                "cacti": int(row["cacti"]),
                "baseline_ms": float(row["baseline_ms"]),
                "faster_ms": float(row["faster_ms"])
            })

    return results


def plot_experiment(
    results,
    experiment,
    x_column,
    x_label,
    title,
    filename
):
    """
    Create a graph comparing the running times
    of the two algorithms for one experiment.
    """

    # Get only the results for this experiment.
    data = [
        row for row in results
        if row["experiment"] == experiment
    ]

    if not data:
        raise ValueError(
            f"No benchmark results found for {experiment}"
        )

    # Sort the results by the variable on the x-axis.
    data.sort(key=lambda row: row[x_column])

    # Extract the x-axis values and running times.
    x_values = [row[x_column] for row in data]

    baseline_times = [
        row["baseline_ms"] for row in data
    ]

    faster_times = [
        row["faster_ms"] for row in data
    ]

    # A logarithmic axis requires positive measurements.
    if any(
        time <= 0
        for time in baseline_times + faster_times
    ):
        raise ValueError(
            "Running times must be positive. "
            "Run the benchmark again."
        )

    # Create a new figure for this experiment.
    fig, ax = plt.subplots(figsize=(9, 5))

    # Plot the baseline running times.
    ax.plot(
        x_values,
        baseline_times,
        marker="o",
        linewidth=2,
        label="Baseline (Exhaustive Search)"
    )

    # Plot the faster algorithm running times.
    ax.plot(
        x_values,
        faster_times,
        marker="s",
        linewidth=2,
        label="Faster (Cactus Subsets)"
    )

    # Add the graph title and axis labels.
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Running Time (milliseconds)")

    # Use logarithmic scale because running times
    # can differ by several orders of magnitude.
    ax.set_yscale("log")

    # Display whole numbers on the x-axis.
    ax.xaxis.set_major_locator(
        MaxNLocator(integer=True)
    )

    # Add grid lines to make comparisons easier.
    ax.grid(
        True,
        which="both",
        linestyle="--",
        alpha=0.4
    )

    # Display labels identifying both algorithms.
    ax.legend()

    # Prevent labels from getting cut off.
    fig.tight_layout()

    # Save the graph as a high-resolution PNG.
    output_path = OUTPUT_DIR / filename

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    # Close the figure to free memory.
    plt.close(fig)

    print(f"Saved graph: {output_path}")


def main():

    # Load the benchmark measurements.
    results = load_results()

    # Make sure the results directory exists.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Experiment 1:
    # Change the sprinkler count while fixing cacti.
    plot_experiment(
        results,
        experiment="vary_sprinklers",
        x_column="sprinklers",
        x_label="Number of Sprinklers",
        title="Running Time vs Number of Sprinklers",
        filename="plot_vary_sprinklers.png"
    )

    # Experiment 2:
    # Change the cactus count while fixing sprinklers.
    plot_experiment(
        results,
        experiment="vary_cacti",
        x_column="cacti",
        x_label="Number of Cacti",
        title="Running Time vs Number of Cacti",
        filename="plot_vary_cacti.png"
    )

    print("\nAll performance graphs generated.")


if __name__ == "__main__":
    main()