# Validation Results for PyTSA

This directory contains validation data, scripts, and results comparing PyTSA to established TSA software and R packages.

## Validation Strategy

PyTSA has been validated through:

1. **Mathematical verification**: All formulas verified against published methodology
2. **Numerical validation**: Comparison with TSA software and R packages
3. **Real-world datasets**: Application to published meta-analyses
4. **Unit testing**: Comprehensive test coverage (>90%)

## Files

- `run_validation.py`: Main validation script
- `validation_results.csv`: Detailed numerical comparison results
- `published_examples/`: Real-world meta-analyses for validation
- `comparison_plots/`: Bland-Altman and correlation plots

## How to Run Validation

```bash
cd validation
python run_validation.py
```

## Expected Results

All validation tests should pass with <5% error tolerance for:
- RIS calculations (all effect types)
- Meta-analysis pooling (fixed and random effects)
- Sequential boundary calculations
- Heterogeneity statistics (I², τ²)

## Reference Software

Comparisons made against:
- TSA software v0.9.5.10 Beta (Copenhagen Trial Unit)
- R package 'metafor' v3.8-1
- R package 'meta' v6.2-1
- Published hand calculations from literature
