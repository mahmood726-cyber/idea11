#!/usr/bin/env python3
"""
Basic PyTSA Example: Dichotomous Outcome Analysis

This example demonstrates a complete Trial Sequential Analysis
for a dichotomous outcome (mortality).
"""

from pytsa import TSAAnalyzer
from pytsa.data import load_example
import matplotlib.pyplot as plt


def main():
    print("=" * 70)
    print("PyTSA Example: Trial Sequential Analysis for Mortality Reduction")
    print("=" * 70)
    print()

    # Load example dataset
    print("Loading example data...")
    data = load_example('dichotomous')
    print(f"Loaded {len(data)} studies spanning {data['year'].min()}-{data['year'].max()}")
    print()

    # Display data summary
    total_events_t = data['events_treatment'].sum()
    total_n_t = data['n_treatment'].sum()
    total_events_c = data['events_control'].sum()
    total_n_c = data['n_control'].sum()

    print("Data Summary:")
    print(f"  Treatment group: {total_events_t}/{total_n_t} events ({total_events_t/total_n_t:.1%})")
    print(f"  Control group: {total_events_c}/{total_n_c} events ({total_events_c/total_n_c:.1%})")
    print()

    # Configure TSA
    print("Configuring Trial Sequential Analysis...")
    analyzer = TSAAnalyzer(
        alpha=0.05,               # Two-sided 5% significance level
        beta=0.20,                # 20% type II error (80% power)
        effect_type='risk_ratio', # Analyzing risk ratios
        model='random_effects',   # Random-effects model
        boundary='lan_demets_obf', # Lan-DeMets O'Brien-Fleming boundary
        heterogeneity_adjustment=True  # Adjust RIS for heterogeneity
    )
    print("  Alpha: 0.05 (two-sided)")
    print("  Power: 80% (beta = 0.20)")
    print("  Model: Random-effects")
    print("  Boundary: Lan-DeMets O'Brien-Fleming")
    print()

    # Perform TSA
    print("Performing Trial Sequential Analysis...")
    results = analyzer.fit(
        data=data,
        target_effect=0.75,       # Target: 25% relative risk reduction (RR = 0.75)
        control_event_rate=0.18   # Assumed control event rate: 18%
    )
    print("Analysis complete!")
    print()

    # Display results summary
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()
    print(f"Required Information Size (RIS): {results.ris:.0f}")
    print(f"Accrued information: {results.data['total_n'].iloc[-1]:.0f}")
    print(f"Information fraction: {results.interpretation['information_fraction']:.1%}")
    print()
    print(f"Pooled Risk Ratio: {results.interpretation['final_effect']:.3f}")
    print(f"95% CI: [{results.interpretation['final_ci_lower']:.3f}, "
          f"{results.interpretation['final_ci_upper']:.3f}]")
    print(f"P-value: {results.interpretation['final_p_value']:.4f}")
    print()
    print(f"Heterogeneity I²: {results.interpretation['heterogeneity_I2']:.1f}%")
    print(f"Between-study variance τ²: {results.interpretation['heterogeneity_tau2']:.4f}")
    print()
    print(f"RIS reached: {'Yes' if results.interpretation['ris_reached'] else 'No'}")
    print(f"Efficacy boundary crossed: {'Yes' if results.interpretation['efficacy_crossed'] else 'No'}")
    print(f"Futility boundary crossed: {'Yes' if results.interpretation['futility_crossed'] else 'No'}")
    print()
    print("CONCLUSION:")
    print(f"  {results.interpretation['conclusion']}")
    print()

    # Create visualization
    print("Creating TSA plot...")
    fig = results.plot(figsize=(12, 8))

    # Save plot
    output_file = 'tsa_plot_example.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    print()

    # Export detailed results
    output_csv = 'tsa_results_example.csv'
    results.to_dataframe().to_csv(output_csv, index=False)
    print(f"Detailed results saved to: {output_csv}")
    print()

    # Interpretation guide
    print("=" * 70)
    print("INTERPRETATION GUIDE")
    print("=" * 70)
    print()

    if results.interpretation['firm_evidence']:
        print("✓ CONCLUSIVE EVIDENCE")
        if results.interpretation['efficacy_crossed']:
            print("  The intervention shows a significant effect.")
            print("  The efficacy boundary was crossed, indicating firm evidence")
            print("  for effectiveness while controlling for repeated testing.")
        elif results.interpretation['ris_reached']:
            if results.interpretation['final_p_value'] < analyzer.alpha:
                print("  The RIS was reached with a significant effect.")
                print("  This meta-analysis has adequate power and shows")
                print("  a significant treatment effect.")
            else:
                print("  The RIS was reached without a significant effect.")
                print("  This adequately powered meta-analysis does not show")
                print("  a significant treatment effect.")
    else:
        print("⚠ INCONCLUSIVE EVIDENCE")
        print("  More information is needed to draw firm conclusions.")
        print("  The current evidence is insufficient and may be unreliable.")

        # Calculate how much more information is needed
        remaining_fraction = 1.0 - results.interpretation['information_fraction']
        remaining_n = results.ris * remaining_fraction
        print()
        print(f"  Approximately {remaining_n:.0f} more participants needed")
        print(f"  to reach the Required Information Size.")

    print()
    print("=" * 70)
    print("Analysis complete! See plot and CSV file for details.")
    print("=" * 70)


if __name__ == '__main__':
    main()
