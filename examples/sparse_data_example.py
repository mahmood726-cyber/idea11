#!/usr/bin/env python3
"""
PyTSA Example: Handling Sparse Data and Rare Events

This example demonstrates TSA for rare adverse events,
comparing different sparse data handling methods.
"""

from pytsa import TSAAnalyzer
from pytsa.data import load_example
from pytsa.sparse_data import identify_sparse_data
import matplotlib.pyplot as plt


def main():
    print("=" * 70)
    print("PyTSA Example: Sparse Data Analysis (Rare Adverse Events)")
    print("=" * 70)
    print()

    # Load sparse data example
    print("Loading sparse data example...")
    data = load_example('sparse')
    print(f"Loaded {len(data)} studies")
    print()

    # Analyze data sparsity
    print("Data Characteristics:")
    total_events_t = data['events_treatment'].sum()
    total_n_t = data['n_treatment'].sum()
    total_events_c = data['events_control'].sum()
    total_n_c = data['n_control'].sum()

    rate_t = total_events_t / total_n_t
    rate_c = total_events_c / total_n_c

    print(f"  Treatment group: {total_events_t}/{total_n_t} events ({rate_t:.2%})")
    print(f"  Control group: {total_events_c}/{total_n_c} events ({rate_c:.2%})")
    print()

    # Identify sparse studies
    sparse_mask = identify_sparse_data(data, threshold=0.05)
    n_sparse = sparse_mask.sum()
    print(f"  Studies with event rate < 5%: {n_sparse}/{len(data)}")
    print(f"  Studies with zero events: {((data['events_treatment'] == 0) | (data['events_control'] == 0)).sum()}")
    print()

    # Compare different sparse data methods
    print("=" * 70)
    print("Comparing Sparse Data Handling Methods")
    print("=" * 70)
    print()

    methods = [
        ('No adjustment', None),
        ('Continuity correction', 'continuity_correction'),
        ('Beta-binomial model', 'beta_binomial')
    ]

    results_dict = {}

    for method_name, method_code in methods:
        print(f"Method: {method_name}")
        print("-" * 50)

        # Configure analyzer
        analyzer = TSAAnalyzer(
            alpha=0.05,
            beta=0.20,
            effect_type='odds_ratio',  # OR often used for rare events
            model='random_effects',
            boundary='lan_demets_obf',
            heterogeneity_adjustment=True,
            sparse_data_method=method_code
        )

        # Perform TSA
        results = analyzer.fit(
            data=data,
            target_effect=0.50,       # Target: 50% reduction (OR = 0.5)
            control_event_rate=0.015  # Expected control rate: 1.5%
        )

        results_dict[method_name] = results

        # Display key results
        print(f"  RIS: {results.ris:.0f}")
        print(f"  Pooled OR: {results.interpretation['final_effect']:.3f}")
        print(f"  95% CI: [{results.interpretation['final_ci_lower']:.3f}, "
              f"{results.interpretation['final_ci_upper']:.3f}]")
        print(f"  P-value: {results.interpretation['final_p_value']:.4f}")
        print(f"  I²: {results.interpretation['heterogeneity_I2']:.1f}%")
        print(f"  Conclusion: {results.interpretation['conclusion']}")
        print()

    # Create comparison visualization
    print("Creating comparison plots...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for idx, (method_name, results) in enumerate(results_dict.items()):
        ax = axes[idx]

        # Extract data for plotting
        x = results.data['total_n']
        z = results.data['z_score']
        upper = results.data['upper_boundary']
        lower = results.data['lower_boundary']
        ris = results.ris

        # Plot
        ax.axvline(ris, color='black', linestyle='--', linewidth=2, alpha=0.7)
        ax.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
        ax.plot(x, z, 'o-', color='blue', linewidth=2.5, markersize=6)

        mask = x <= ris
        ax.plot(x[mask], upper[mask], '-', color='red', linewidth=2, alpha=0.8)
        ax.plot(x[mask], lower[mask], '-', color='red', linewidth=2, alpha=0.8)

        ax.set_title(f'{method_name}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Cumulative Sample Size', fontsize=10)
        ax.set_ylabel('Cumulative Z-score', fontsize=10)
        ax.grid(True, alpha=0.3)

        # Add text annotation
        info_text = f"RIS: {ris:.0f}\nOR: {results.interpretation['final_effect']:.3f}"
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    output_file = 'tsa_sparse_data_comparison.png'
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Comparison plot saved to: {output_file}")
    print()

    # Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS FOR SPARSE DATA")
    print("=" * 70)
    print()
    print("When to use different methods:")
    print()
    print("1. Continuity Correction (add 0.5):")
    print("   - Quick and simple")
    print("   - Standard approach in most meta-analyses")
    print("   - May be biased when events are very rare")
    print()
    print("2. Beta-Binomial Model:")
    print("   - More principled statistical approach")
    print("   - Better for very rare events (< 1%)")
    print("   - Shrinks estimates toward pooled rate")
    print("   - Recommended for serious adverse events")
    print()
    print("3. No Adjustment:")
    print("   - Only when events are not too rare (> 5%)")
    print("   - Will fail if zero events in any study")
    print()

    # Additional recommendations
    if rate_c < 0.01 or rate_t < 0.01:
        print("⚠ WARNING: Event rates < 1%")
        print("  Consider:")
        print("  - Using beta-binomial model")
        print("  - Peto OR method (not yet implemented)")
        print("  - Individual patient data meta-analysis")
        print()

    print("=" * 70)
    print("Analysis complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
