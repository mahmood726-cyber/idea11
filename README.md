# PyTSA: Python Trial Sequential Analysis Platform

A comprehensive Python implementation of Trial Sequential Analysis (TSA) for meta-analysis, providing robust statistical methods for controlling type I and type II errors in cumulative meta-analyses.

## Features

- **Core TSA Methods**: Required Information Size (RIS) calculation, alpha-spending functions
- **Sequential Monitoring Boundaries**: O'Brien-Fleming, Lan-DeMets, and custom boundary implementations
- **Multiple Effect Models**: Fixed-effect and random-effects meta-analysis models
- **Sparse Data Handling**: Beta-binomial and continuity correction methods for rare events
- **Advanced Features**:
  - Bonferroni adjustment for multiple comparisons
  - Heterogeneity adjustment (diversity-adjusted RIS)
  - Publication bias assessment
- **Visualization**: Comprehensive TSA plots with monitoring boundaries and Z-curves

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from pytsa import TSAAnalyzer
from pytsa.data import load_example

# Load example dataset
data = load_example('dichotomous')

# Perform TSA
analyzer = TSAAnalyzer(
    alpha=0.05,
    beta=0.20,
    effect_type='risk_ratio',
    model='random_effects'
)

results = analyzer.fit(data)
results.plot()
```

## Documentation

See `docs/` for full documentation and API reference.

## Citation

If you use PyTSA in your research, please cite our methods paper (see `METHODS_PAPER.md`).

## License

MIT License
