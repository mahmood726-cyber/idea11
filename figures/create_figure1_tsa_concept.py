"""
Create Figure 1: TSA Conceptual Diagram for Synthesis Paper
Shows Z-curve, monitoring boundaries, RIS, and conclusive/inconclusive scenarios
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Common parameters
ris = 3000
alpha = 0.05
z_alpha = 1.96

# Figure 1A: Conclusive Evidence (Efficacy Boundary Crossed)
# Generate cumulative sample sizes
n_studies_a = 15
sample_sizes_a = np.array([120, 180, 250, 320, 400, 520, 680, 850, 1050, 1280, 1520, 1780, 2050, 2340, 2650])
info_fractions_a = sample_sizes_a / ris

# O'Brien-Fleming boundaries
obf_boundaries_a = z_alpha / np.sqrt(info_fractions_a)
obf_boundaries_lower_a = -obf_boundaries_a

# Z-curve (crosses efficacy boundary at study 11)
z_scores_a = np.array([0.5, 1.2, 1.8, 2.3, 2.6, 2.9, 3.2, 3.4, 3.5, 3.6, 3.7, 3.8, 3.85, 3.9, 3.92])

# Plot boundaries
ax1.plot(sample_sizes_a, obf_boundaries_a, 'r--', linewidth=2.5, label='Efficacy boundary', alpha=0.8)
ax1.plot(sample_sizes_a, obf_boundaries_lower_a, 'r--', linewidth=2.5, alpha=0.8)

# Futility boundaries (inner wedge)
futility_upper = obf_boundaries_a * 0.5
futility_lower = obf_boundaries_lower_a * 0.5
ax1.fill_between(sample_sizes_a, futility_lower, futility_upper, alpha=0.15, color='orange', label='Futility area')

# Plot Z-curve
ax1.plot(sample_sizes_a, z_scores_a, 'b-', linewidth=3, marker='o', markersize=6, label='Z-curve', zorder=5)

# Highlight boundary crossing
crossing_idx = 10
ax1.scatter(sample_sizes_a[crossing_idx], z_scores_a[crossing_idx],
           s=300, c='red', marker='*', zorder=10, edgecolors='darkred', linewidths=2,
           label='Boundary crossed')

# RIS line
ax1.axvline(ris, color='green', linestyle=':', linewidth=2.5, alpha=0.7, label=f'RIS ({ris} patients)')

# Conventional significance line
ax1.axhline(z_alpha, color='gray', linestyle='-.', linewidth=1.5, alpha=0.5, label='p=0.05 (conventional)')
ax1.axhline(-z_alpha, color='gray', linestyle='-.', linewidth=1.5, alpha=0.5)

# Formatting
ax1.set_xlabel('Cumulative Sample Size (n)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Z-score', fontsize=12, fontweight='bold')
ax1.set_title('A. Conclusive Evidence:\nEfficacy Boundary Crossed', fontsize=13, fontweight='bold', pad=15)
ax1.legend(loc='upper right', fontsize=9, framealpha=0.95)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(-5, 5)
ax1.set_xlim(0, 3200)

# Add annotation
ax1.annotate('Conclusive for benefit\n(Type I error controlled)',
            xy=(sample_sizes_a[crossing_idx], z_scores_a[crossing_idx]),
            xytext=(1800, 4.2),
            fontsize=10, fontweight='bold', color='darkred',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkred'))


# Figure 1B: Inconclusive Evidence (RIS not reached)
# Generate cumulative sample sizes (stopped early)
n_studies_b = 12
sample_sizes_b = np.array([120, 180, 250, 320, 400, 520, 680, 850, 1050, 1280, 1520, 1780])
info_fractions_b = sample_sizes_b / ris

# O'Brien-Fleming boundaries
obf_boundaries_b = z_alpha / np.sqrt(info_fractions_b)
obf_boundaries_lower_b = -obf_boundaries_b

# Z-curve (stays below boundary, p<0.05 but inconclusive)
z_scores_b = np.array([0.3, 0.8, 1.4, 1.7, 1.9, 2.1, 2.2, 2.3, 2.35, 2.4, 2.42, 2.45])

# Plot boundaries
ax2.plot(sample_sizes_b, obf_boundaries_b, 'r--', linewidth=2.5, label='Efficacy boundary', alpha=0.8)
ax2.plot(sample_sizes_b, obf_boundaries_lower_b, 'r--', linewidth=2.5, alpha=0.8)

# Futility boundaries
futility_upper_b = obf_boundaries_b * 0.5
futility_lower_b = obf_boundaries_lower_b * 0.5
ax2.fill_between(sample_sizes_b, futility_lower_b, futility_upper_b, alpha=0.15, color='orange', label='Futility area')

# Plot Z-curve
ax2.plot(sample_sizes_b, z_scores_b, 'b-', linewidth=3, marker='o', markersize=6, label='Z-curve', zorder=5)

# RIS line
ax2.axvline(ris, color='green', linestyle=':', linewidth=2.5, alpha=0.7, label=f'RIS ({ris} patients)')

# Conventional significance line
ax2.axhline(z_alpha, color='gray', linestyle='-.', linewidth=1.5, alpha=0.5, label='p=0.05 (conventional)')
ax2.axhline(-z_alpha, color='gray', linestyle='-.', linewidth=1.5, alpha=0.5)

# Shade the inconclusive region
ax2.axvspan(sample_sizes_b[-1], ris, alpha=0.2, color='red', label='Additional evidence needed')

# Formatting
ax2.set_xlabel('Cumulative Sample Size (n)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Z-score', fontsize=12, fontweight='bold')
ax2.set_title('B. Inconclusive Evidence:\nRIS Not Reached', fontsize=13, fontweight='bold', pad=15)
ax2.legend(loc='upper right', fontsize=9, framealpha=0.95)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(-5, 5)
ax2.set_xlim(0, 3200)

# Add annotations
ax2.annotate(f'p<0.05 but inconclusive\n(59% of RIS)',
            xy=(sample_sizes_b[-1], z_scores_b[-1]),
            xytext=(1000, 3.8),
            fontsize=10, fontweight='bold', color='darkblue',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7),
            arrowprops=dict(arrowstyle='->', lw=2, color='darkblue'))

ax2.annotate(f'Need ~{ris - sample_sizes_b[-1]} more patients',
            xy=(ris, 0),
            xytext=(2400, -3.5),
            fontsize=9, style='italic', color='darkgreen',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.6),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='darkgreen'))

plt.tight_layout()
plt.savefig('/home/user/idea11/figures/Figure1_TSA_Concept.png', dpi=300, bbox_inches='tight')
plt.savefig('/home/user/idea11/figures/Figure1_TSA_Concept.pdf', bbox_inches='tight')
print("Figure 1 saved: Figure1_TSA_Concept.png and .pdf")
plt.close()
