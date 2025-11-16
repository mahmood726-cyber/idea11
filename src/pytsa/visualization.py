"""
Visualization components for TSA plots.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .results import TSAResults

sns.set_style("whitegrid")


class TSAPlotter:
    """Create Trial Sequential Analysis visualizations."""

    def __init__(self, results: 'TSAResults'):
        self.results = results
        self.data = results.data
        self.ris = results.ris

    def plot(
        self,
        show_z_curve: bool = True,
        show_boundaries: bool = True,
        show_futility: bool = True,
        figsize: tuple = (12, 8),
        save_path: Optional[str] = None
    ):
        """
        Create comprehensive TSA plot.

        Parameters
        ----------
        show_z_curve : bool
            Show cumulative Z-curve
        show_boundaries : bool
            Show efficacy monitoring boundaries
        show_futility : bool
            Show futility boundaries
        figsize : tuple
            Figure size (width, height)
        save_path : str, optional
            Path to save figure

        Returns
        -------
        matplotlib.figure.Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # X-axis: cumulative sample size
        x = self.data['total_n']

        # Plot RIS vertical line
        ax.axvline(self.ris, color='black', linestyle='--', linewidth=2,
                   label=f'RIS = {self.ris:.0f}', alpha=0.7)

        # Plot horizontal line at z=0
        ax.axhline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

        # Plot Z-curve
        if show_z_curve:
            z_scores = self.data['z_score']
            ax.plot(x, z_scores, 'o-', color='blue', linewidth=2.5,
                   markersize=6, label='Cumulative Z-score', zorder=5)

        # Plot efficacy boundaries
        if show_boundaries:
            upper = self.data['upper_boundary']
            lower = self.data['lower_boundary']

            # Only plot up to RIS
            mask = x <= self.ris
            ax.plot(x[mask], upper[mask], '-', color='red', linewidth=2,
                   label='Efficacy boundary', alpha=0.8)
            ax.plot(x[mask], lower[mask], '-', color='red', linewidth=2, alpha=0.8)

            # Shade efficacy regions
            ax.fill_between(x[mask], upper[mask], 10, color='red', alpha=0.1)
            ax.fill_between(x[mask], lower[mask], -10, color='red', alpha=0.1)

        # Plot futility boundaries
        if show_futility and 'futility_upper' in self.data.columns:
            fut_upper = self.data['futility_upper']
            fut_lower = self.data['futility_lower']

            mask = x <= self.ris
            ax.plot(x[mask], fut_upper[mask], '--', color='orange',
                   linewidth=1.5, label='Futility boundary', alpha=0.7)
            ax.plot(x[mask], fut_lower[mask], '--', color='orange',
                   linewidth=1.5, alpha=0.7)

            # Shade futility region
            ax.fill_between(x[mask], fut_upper[mask], fut_lower[mask],
                          color='yellow', alpha=0.1)

        # Labels and title
        ax.set_xlabel('Cumulative Sample Size', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cumulative Z-score', fontsize=12, fontweight='bold')

        title = 'Trial Sequential Analysis\n'
        title += f'{self.results.effect_type.replace("_", " ").title()} | '
        title += f'{self.results.model_type.replace("_", " ").title()}'
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Set axis limits
        y_max = max(
            self.data['upper_boundary'].max() * 1.2,
            abs(self.data['z_score']).max() * 1.2
        )
        ax.set_ylim(-y_max, y_max)
        ax.set_xlim(0, max(x.max(), self.ris) * 1.1)

        # Legend
        ax.legend(loc='best', frameon=True, shadow=True, fontsize=10)

        # Grid
        ax.grid(True, alpha=0.3)

        # Add text box with interpretation
        interpretation_text = self._format_interpretation()
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, interpretation_text, transform=ax.transAxes,
               fontsize=9, verticalalignment='top', bbox=props,
               family='monospace')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        return fig

    def _format_interpretation(self) -> str:
        """Format interpretation for plot annotation."""
        interp = self.results.interpretation

        lines = []
        lines.append("TSA INTERPRETATION")
        lines.append("-" * 30)
        lines.append(f"RIS reached: {'Yes' if interp['ris_reached'] else 'No'}")
        lines.append(f"Efficacy crossed: {'Yes' if interp['efficacy_crossed'] else 'No'}")
        lines.append(f"Futility crossed: {'Yes' if interp['futility_crossed'] else 'No'}")
        lines.append(f"Evidence: {'Conclusive' if interp['firm_evidence'] else 'Inconclusive'}")

        return "\n".join(lines)

    def plot_forest(self, figsize: tuple = (10, 8)):
        """
        Create forest plot showing individual study effects.

        Returns
        -------
        matplotlib.figure.Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Get individual study effects from cumulative results
        # This is simplified - in practice would need original study data

        ax.set_title('Forest Plot of Individual Studies',
                    fontsize=14, fontweight='bold')

        # Placeholder - would need to implement with actual study data
        ax.text(0.5, 0.5, 'Forest plot requires individual study data',
               ha='center', va='center', transform=ax.transAxes)

        return fig
