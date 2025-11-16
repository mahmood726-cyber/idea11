# PyTSA Tutorial: Step-by-Step Guide

This tutorial will walk you through conducting a Trial Sequential Analysis using PyTSA.

## Table of Contents

1. [Installation](#installation)
2. [Basic Concepts](#basic-concepts)
3. [Example 1: Dichotomous Outcomes](#example-1-dichotomous-outcomes)
4. [Example 2: Continuous Outcomes](#example-2-continuous-outcomes)
5. [Example 3: Handling Sparse Data](#example-3-handling-sparse-data)
6. [Example 4: Multiple Outcomes with Bonferroni](#example-4-multiple-outcomes-with-bonferroni)
7. [Interpreting Results](#interpreting-results)
8. [Customizing Visualizations](#customizing-visualizations)

## Installation

```bash
# Install from source
git clone https://github.com/pytsa/pytsa.git
cd pytsa
pip install -e .

# Or install from PyPI (when available)
# pip install pytsa
```

## Basic Concepts

Before diving into examples, let's understand the key TSA concepts:

### What is TSA?

Trial Sequential Analysis controls type I and type II errors in cumulative meta-analyses by:

1. **Calculating Required Information Size (RIS)**: The total sample size needed to detect a target effect with specified power
2. **Setting monitoring boundaries**: Critical values that account for repeated testing
3. **Sequential monitoring**: Checking boundaries as each new study is added
4. **Determining conclusiveness**: Identifying when evidence is sufficient

### When to Use TSA?

Use TSA when:
- Conducting or updating a meta-analysis
- Want to control for random error in cumulative analysis
- Need to determine if more studies are needed
- Want to avoid false positive results from repeated testing
- Planning sample size for future studies

## Example 1: Dichotomous Outcomes

Let's analyze a meta-analysis of mortality reduction with a new drug.

### Step 1: Load Data

```python
from pytsa import TSAAnalyzer
from pytsa.data import load_example
import pandas as pd

# Load example dichotomous data
data = load_example('dichotomous')

# View the data structure
print(data.head())
```

Output:
```
  study_id  year  events_treatment  n_treatment  events_control  n_control
0  Study_01  2005                12          100              18        100
1  Study_02  2006                15          120              22        120
2  Study_03  2007                 8           80              15         80
```

### Step 2: Configure TSA

```python
# Create analyzer
analyzer = TSAAnalyzer(
    alpha=0.05,              # Two-sided significance level
    beta=0.20,               # Type II error (80% power)
    effect_type='risk_ratio', # RR, OR, or RD
    model='random_effects',   # Fixed or random effects
    boundary='lan_demets_obf', # Monitoring boundary type
    heterogeneity_adjustment=True  # Adjust RIS for heterogeneity
)
```

### Step 3: Perform Analysis

```python
# Run TSA
results = analyzer.fit(
    data=data,
    target_effect=0.75,       # Target RR = 0.75 (25% reduction)
    control_event_rate=0.18   # Expected control mortality = 18%
)
```

### Step 4: View Results

```python
# Print summary
print(results.summary())

# Create TSA plot
fig = results.plot()
fig.savefig('tsa_plot.png', dpi=300)

# Export detailed results
df = results.to_dataframe()
df.to_csv('tsa_results.csv', index=False)
```

### Step 5: Interpret

```python
# Check key interpretations
print(f"Conclusion: {results.interpretation['conclusion']}")
print(f"RIS reached: {results.interpretation['ris_reached']}")
print(f"Efficacy boundary crossed: {results.interpretation['efficacy_crossed']}")
print(f"Final effect: {results.interpretation['final_effect']:.3f}")
print(f"Information fraction: {results.interpretation['information_fraction']:.1%}")
```

## Example 2: Continuous Outcomes

Analyzing blood pressure reduction with antihypertensive drugs.

```python
from pytsa import TSAAnalyzer
from pytsa.data import load_example

# Load continuous outcome data
data = load_example('continuous')

# Configure for mean difference
analyzer = TSAAnalyzer(
    alpha=0.05,
    beta=0.20,
    effect_type='mean_difference',
    model='random_effects',
    boundary='lan_demets_obf'
)

# Fit model
results = analyzer.fit(
    data=data,
    target_effect=-5.0,      # Target reduction of 5 mmHg
    variance_estimate=150.0  # Estimated variance
)

# View results
print(results.summary())
results.plot()
```

### Using Standardized Mean Difference

For different measurement scales across studies:

```python
analyzer = TSAAnalyzer(
    alpha=0.05,
    beta=0.20,
    effect_type='standardized_mean_difference',  # Cohen's d / Hedges' g
    model='random_effects'
)

results = analyzer.fit(
    data=data,
    target_effect=0.5  # Medium effect size
)
```

## Example 3: Handling Sparse Data

When analyzing rare events (e.g., serious adverse events):

```python
from pytsa import TSAAnalyzer
from pytsa.data import load_example

# Load sparse data (rare events)
data = load_example('sparse')

# Check event rates
print(f"Treatment event rate: {data['events_treatment'].sum() / data['n_treatment'].sum():.1%}")
print(f"Control event rate: {data['events_control'].sum() / data['n_control'].sum():.1%}")

# Configure with sparse data handling
analyzer = TSAAnalyzer(
    alpha=0.05,
    beta=0.20,
    effect_type='odds_ratio',
    model='random_effects',
    sparse_data_method='beta_binomial'  # Or 'continuity_correction'
)

results = analyzer.fit(
    data=data,
    target_effect=0.50,      # Target OR = 0.5 (50% reduction)
    control_event_rate=0.015 # 1.5% baseline rate
)

print(results.summary())
```

### Comparing Sparse Data Methods

```python
# Method 1: Continuity correction
analyzer_cc = TSAAnalyzer(
    alpha=0.05, beta=0.20, effect_type='odds_ratio',
    sparse_data_method='continuity_correction'
)
results_cc = analyzer_cc.fit(data, target_effect=0.50, control_event_rate=0.015)

# Method 2: Beta-binomial
analyzer_bb = TSAAnalyzer(
    alpha=0.05, beta=0.20, effect_type='odds_ratio',
    sparse_data_method='beta_binomial'
)
results_bb = analyzer_bb.fit(data, target_effect=0.50, control_event_rate=0.015)

# Compare results
print(f"Continuity correction RIS: {results_cc.ris:.0f}")
print(f"Beta-binomial RIS: {results_bb.ris:.0f}")
```

## Example 4: Multiple Outcomes with Bonferroni

When analyzing multiple outcomes (e.g., mortality, MI, stroke):

```python
from pytsa import TSAAnalyzer
from pytsa.data import load_example

# Load data for each outcome
data_mortality = load_example('dichotomous')
# data_mi = load_example('mi')  # Hypothetical
# data_stroke = load_example('stroke')  # Hypothetical

# Apply Bonferroni adjustment for 3 outcomes
analyzer = TSAAnalyzer(
    alpha=0.05,
    beta=0.20,
    effect_type='risk_ratio',
    model='random_effects',
    bonferroni_k=3  # Adjusted alpha = 0.05/3 = 0.0167
)

# Analyze each outcome
results_mortality = analyzer.fit(
    data=data_mortality,
    target_effect=0.75,
    control_event_rate=0.18
)

print(f"Adjusted alpha: {analyzer.adjusted_alpha:.4f}")
print(results_mortality.summary())
```

## Interpreting Results

### Understanding the TSA Plot

The TSA plot shows:

1. **Blue line (Z-curve)**: Cumulative Z-statistic as studies accumulate
2. **Red lines**: Efficacy monitoring boundaries
   - If Z-curve crosses: Significant effect detected (controlling for repeated testing)
3. **Orange dashed lines**: Futility boundaries
   - If Z-curve enters futility region: Intervention unlikely to be effective
4. **Vertical black line**: Required Information Size (RIS)
5. **Shaded regions**:
   - Red: Efficacy region
   - Yellow: Futility region

### Possible Conclusions

#### Scenario 1: Efficacy Boundary Crossed
```
Conclusion: CONCLUSIVE - Evidence for effect (efficacy boundary crossed)
Interpretation: The intervention is effective with controlled type I error
Action: Can stop enrolling studies for this question
```

#### Scenario 2: Futility Boundary Crossed
```
Conclusion: CONCLUSIVE - Evidence for futility (futility boundary crossed)
Interpretation: The intervention is unlikely to achieve target effect
Action: Can stop enrolling studies; intervention not sufficiently effective
```

#### Scenario 3: RIS Reached, Significant Result
```
Conclusion: CONCLUSIVE - RIS reached with significant effect
Interpretation: Adequately powered meta-analysis shows significant effect
Action: Firm evidence for intervention effectiveness
```

#### Scenario 4: RIS Reached, Non-Significant Result
```
Conclusion: CONCLUSIVE - RIS reached, no significant effect
Interpretation: Adequately powered meta-analysis shows no significant effect
Action: Firm evidence that intervention is not effective
```

#### Scenario 5: Inconclusive
```
Conclusion: INCONCLUSIVE - More information needed
Interpretation: Insufficient information to draw firm conclusions
Action: More studies needed; current evidence is unreliable
```

### Key Metrics to Report

When reporting TSA results, include:

1. **RIS and information fraction**
   ```python
   print(f"RIS: {results.ris:.0f}")
   print(f"Accrued information: {results.interpretation['final_effect']:.0f}")
   print(f"Information fraction: {results.interpretation['information_fraction']:.1%}")
   ```

2. **Boundary crossings**
   ```python
   print(f"Efficacy boundary crossed: {results.interpretation['efficacy_crossed']}")
   print(f"Futility boundary crossed: {results.interpretation['futility_crossed']}")
   ```

3. **Pooled effect estimate**
   ```python
   print(f"Effect: {results.interpretation['final_effect']:.3f}")
   print(f"95% CI: [{results.interpretation['final_ci_lower']:.3f}, "
         f"{results.interpretation['final_ci_upper']:.3f}]")
   ```

4. **Heterogeneity (for random-effects)**
   ```python
   print(f"I²: {results.interpretation['heterogeneity_I2']:.1f}%")
   print(f"τ²: {results.interpretation['heterogeneity_tau2']:.4f}")
   ```

## Customizing Visualizations

### Basic Customization

```python
# Create plot with custom options
fig = results.plot(
    show_z_curve=True,
    show_boundaries=True,
    show_futility=True,
    figsize=(14, 10)
)

# Customize further with matplotlib
import matplotlib.pyplot as plt

ax = fig.gca()
ax.set_title('TSA: Mortality Reduction with New Drug', fontsize=16)
ax.set_xlabel('Cumulative Sample Size', fontsize=14)
plt.tight_layout()
fig.savefig('custom_tsa_plot.png', dpi=300, bbox_inches='tight')
```

### Creating Multiple Plots

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot different outcomes
outcomes = ['mortality', 'mi', 'stroke', 'composite']
results_list = [results_mortality, results_mi, results_stroke, results_composite]

for ax, outcome, result in zip(axes.flat, outcomes, results_list):
    result.plot(ax=ax)
    ax.set_title(f'TSA: {outcome.title()}')

plt.tight_layout()
fig.savefig('multiple_outcomes_tsa.png', dpi=300)
```

## Advanced Usage

### Extracting Detailed Data

```python
# Get full results DataFrame
df = results.to_dataframe()

# Extract specific information
print(df[['step', 'n_studies', 'total_n', 'effect', 'z_score',
          'upper_boundary', 'information_fraction']])

# Export for further analysis
df.to_excel('tsa_detailed_results.xlsx', index=False)
```

### Programmatic Interpretation

```python
# Check if more studies needed
if not results.interpretation['firm_evidence']:
    studies_needed = results.ris - results.interpretation['information_fraction']
    print(f"Approximately {studies_needed:.0f} more participants needed")

# Check heterogeneity level
I2 = results.interpretation['heterogeneity_I2']
if I2 < 25:
    print("Low heterogeneity")
elif I2 < 50:
    print("Moderate heterogeneity")
elif I2 < 75:
    print("Substantial heterogeneity")
else:
    print("Considerable heterogeneity - investigate sources")
```

### Sensitivity Analyses

```python
# Sensitivity to boundary type
boundaries = ['obf', 'lan_demets_obf', 'lan_demets_pocock']

for boundary in boundaries:
    analyzer = TSAAnalyzer(
        alpha=0.05, beta=0.20,
        effect_type='risk_ratio',
        model='random_effects',
        boundary=boundary
    )

    results = analyzer.fit(data, target_effect=0.75, control_event_rate=0.18)
    print(f"\n{boundary}: {results.interpretation['conclusion']}")
```

## Best Practices

1. **Prespecify analysis parameters**: Define α, β, target effect, and RIS before analysis
2. **Report both conventional MA and TSA**: TSA complements, doesn't replace, standard meta-analysis
3. **Use appropriate effect measure**: Match measure to outcome type and clinical interpretation
4. **Apply heterogeneity adjustment**: Use diversity-adjusted RIS for random-effects models
5. **Handle sparse data appropriately**: Use specialized methods for rare events
6. **Adjust for multiple outcomes**: Apply Bonferroni or other corrections when testing multiple outcomes
7. **Update with new studies**: Re-run TSA as new studies become available
8. **Document assumptions**: Report all TSA parameters in publications

## Troubleshooting

### Common Issues

**Issue: RIS is extremely large**
- Check if target effect is too small
- Verify control event rate is reasonable
- Consider if effect size is clinically realistic

**Issue: High heterogeneity (I² > 75%)**
- Investigate sources of heterogeneity
- Consider subgroup analyses
- Use diversity-adjusted RIS
- May need larger RIS to account for heterogeneity

**Issue: Results differ from TSA software**
- Check parameter specifications match exactly
- Verify data ordering (chronological)
- Confirm effect measure transformations
- Check sparse data handling methods

## Further Resources

- **Methods Paper**: See `METHODS_PAPER.md` for detailed statistical methodology
- **API Reference**: Full documentation of all functions and parameters
- **Examples**: Additional examples in `examples/` directory
- **Validation**: See `tests/` for validation against TSA software

## Getting Help

- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share experiences
- **Documentation**: https://pytsa.readthedocs.io
- **Email**: [contact information]

---

*This tutorial is part of PyTSA version 0.1.0*
*Last updated: 2025*
