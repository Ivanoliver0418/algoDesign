# algoDesign

# CMPT 360 — Option 4: Cover

**Ivan Oliver**  
NSID: cpf150  
Student Number: 11383104

## 1. Project Overview

The goal of this project is to select sprinklers that water every orange tree while minimizing the number of cacti watered.

Each sprinkler has a position and radius that determine the interval it waters.

We implemented two exact algorithms:

- **Baseline (`baseline.py`):** Uses exhaustive search to check every possible sprinkler subset and returns the one watering the fewest cacti.
- **Faster Algorithm (`fasterAlgo.py`):** Uses cactus-subset enumeration and bitmasks. It also identifies unavoidable cacti and removes irrelevant sprinklers and cacti to reduce unnecessary combinations.

## 2. Requirements

- Python 3.11 or later
- Matplotlib (only needed to generate graphs)

The algorithms, unit tests, and benchmarks use Python's standard library.

To install Matplotlib:

```bash
python3 -m pip install matplotlib
```

## 3. Input Format

The programs accept a JSON file containing four arrays:

- `O`: Positions of orange trees
- `C`: Positions of cacti
- `S`: Positions of sprinklers
- `R`: Radius of each sprinkler

Example (`examples/optimization_example.json`):

```json
{
  "O": [2, 6],
  "C": [4],
  "S": [2, 6, 4],
  "R": [0, 0, 2]
}
```

Each sprinkler `i` waters the inclusive interval `[S[i] - R[i], S[i] + R[i]]`.

## 4. Running the Algorithms

Run these commands from the main project directory.

**Baseline:**

```bash
python3 baseline.py examples/optimization_example.json
```

**Faster Algorithm:**

```bash
python3 fasterAlgo.py examples/optimization_example.json
```

Expected output for both:

```text
Selected indices (0-based): [0, 1]
Selected sprinkler positions: [2, 6]
Number of cacti watered: 0
```

To run the assignment example:

```bash
python3 baseline.py examples/course_example.json
python3 fasterAlgo.py examples/course_example.json
```

Both return sprinkler indices `[0, 1, 2]` and a minimum cost of 2 cacti, following the interval definition in the assignment.

## 5. Running the Tests

To run all unit tests:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover interval boundaries, invalid inputs, overlapping sprinklers, and cases where no valid solution exists.

We also compare the faster algorithm against the baseline using 100 reproducible random inputs.

The current test suite contains 17 tests.

## 6. Running the Experiments

**Basic benchmark:**

```bash
python3 experiments/benchmark.py
```

Compares running times as the number of sprinklers and cacti changes. Results are saved to `results/benchmark.csv`.

**Advanced benchmark:**

```bash
python3 experiments/advanced_benchmark.py
```

Compares the baseline, original cactus-subset algorithm, and optimized algorithm using unavoidable cacti, optional cacti, and random instances.

Results are saved to `results/advanced_benchmark.csv`.

**Scalability and memory evaluation:**

```bash
python3 experiments/scalability.py
```

Tests increasing problem sizes using a 2-second solver time limit. It measures running time and peak traced Python memory allocations using `tracemalloc`.

Results are saved to `results/scalability.csv`.

## 7. Generating Graphs

To generate the basic performance graphs:

```bash
python3 experiments/plot_results.py
```

To generate the advanced performance graphs:

```bash
python3 experiments/plot_advanced.py
```

The graphs are saved as PNG files in the `results/` folder.

## 8. Project Files

```text
algoDesign/
├── baseline.py
├── fasterAlgo.py
├── README.md
├── gitlog.txt
├── examples/
│   ├── optimization_example.json
│   └── course_example.json
├── tests/
│   ├── test_baseline.py
│   └── test_fasterAlgo.py
├── experiments/
│   ├── benchmark.py
│   ├── advanced_benchmark.py
│   ├── scalability.py
│   ├── plot_results.py
│   └── plot_advanced.py
├── results/
└── report/
```

The `results/` folder contains the experimental measurements and generated graphs.

## 9. Development History

The project was developed incrementally, starting with the baseline algorithm, followed by the faster algorithm, correctness tests, pruning optimizations, and experimental evaluation.

The commit history is available in `gitlog.txt` and on GitHub.

Repository: https://github.com/Ivanoliver0418/algoDesign
