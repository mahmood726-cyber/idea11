"""
TSA Results container and interpretation.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from .visualization import TSAPlotter


class TSAResults:
    """
    Container for Trial Sequential Analysis results.

    Provides methods for interpreting results and creating visualizations.
    """

    def __init__(
        self,
        cumulative_results: pd.DataFrame,
        ris: float,
        boundaries: pd.DataFrame,
        alpha: float,
        beta: float,
        effect_type: str,
        model_type: str,
        bonferroni_adjusted: bool = False
    ):
        self.cumulative_results = cumulative_results
        self.ris = ris
        self.boundaries = boundaries
        self.alpha = alpha
        self.beta = beta
        self.effect_type = effect_type
        self.model_type = model_type
        self.bonferroni_adjusted = bonferroni_adjusted

        # Merge cumulative results with boundaries
        self.data = pd.merge(
            cumulative_results,
            boundaries,
            on='step',
            how='left'
        )

        # Interpret results
        self.interpretation = self._interpret()

    def _interpret(self) -> Dict[str, Any]:
        """Interpret TSA results."""
        final_row = self.data.iloc[-1]

        # Check if RIS is reached
        ris_reached = final_row['total_n'] >= self.ris

        # Check if boundaries are crossed
        efficacy_crossed = (
            (self.data['z_score'] >= self.data['upper_boundary']).any() or
            (self.data['z_score'] <= self.data['lower_boundary']).any()
        )

        futility_crossed = False
        if 'futility_upper' in self.data.columns:
            futility_crossed = (
                ((self.data['z_score'] <= self.data['futility_upper']) &
                 (self.data['z_score'] >= self.data['futility_lower'])).any()
            )

        # Determine conclusion
        if efficacy_crossed:
            conclusion = "CONCLUSIVE: Evidence for effect (efficacy boundary crossed)"
            firm_evidence = True
        elif futility_crossed:
            conclusion = "CONCLUSIVE: Evidence for futility (futility boundary crossed)"
            firm_evidence = True
        elif ris_reached:
            if final_row['p_value'] < self.alpha:
                conclusion = "CONCLUSIVE: RIS reached with significant effect"
                firm_evidence = True
            else:
                conclusion = "CONCLUSIVE: RIS reached, no significant effect"
                firm_evidence = True
        else:
            conclusion = "INCONCLUSIVE: More information needed (RIS not reached, no boundary crossed)"
            firm_evidence = False

        return {
            'conclusion': conclusion,
            'firm_evidence': firm_evidence,
            'ris_reached': ris_reached,
            'efficacy_crossed': efficacy_crossed,
            'futility_crossed': futility_crossed,
            'final_effect': final_row['effect'],
            'final_p_value': final_row['p_value'],
            'final_ci_lower': final_row['ci_lower'],
            'final_ci_upper': final_row['ci_upper'],
            'information_fraction': final_row['information_fraction'],
            'heterogeneity_I2': final_row['I2'],
            'heterogeneity_tau2': final_row['tau2'],
        }

    def summary(self) -> str:
        """Generate a text summary of results."""
        lines = []
        lines.append("=" * 70)
        lines.append("TRIAL SEQUENTIAL ANALYSIS RESULTS")
        lines.append("=" * 70)
        lines.append(f"Model: {self.model_type.replace('_', ' ').title()}")
        lines.append(f"Effect measure: {self.effect_type.replace('_', ' ').title()}")
        lines.append(f"Alpha: {self.alpha:.4f}" +
                    (" (Bonferroni adjusted)" if self.bonferroni_adjusted else ""))
        lines.append(f"Beta: {self.beta:.4f} (Power: {1-self.beta:.1%})")
        lines.append("")

        lines.append("-" * 70)
        lines.append("INFORMATION SIZE")
        lines.append("-" * 70)
        lines.append(f"Required Information Size (RIS): {self.ris:.1f}")
        lines.append(f"Accrued information: {self.interpretation['final_effect']:.1f}")
        lines.append(f"Information fraction: {self.interpretation['information_fraction']:.1%}")
        lines.append(f"RIS reached: {'Yes' if self.interpretation['ris_reached'] else 'No'}")
        lines.append("")

        lines.append("-" * 70)
        lines.append("POOLED EFFECT ESTIMATE")
        lines.append("-" * 70)
        lines.append(f"Effect: {self.interpretation['final_effect']:.4f}")
        lines.append(f"95% CI: [{self.interpretation['final_ci_lower']:.4f}, "
                    f"{self.interpretation['final_ci_upper']:.4f}]")
        lines.append(f"P-value: {self.interpretation['final_p_value']:.4f}")
        lines.append("")

        if self.model_type == 'random_effects':
            lines.append("-" * 70)
            lines.append("HETEROGENEITY")
            lines.append("-" * 70)
            lines.append(f"I²: {self.interpretation['heterogeneity_I2']:.1f}%")
            lines.append(f"τ²: {self.interpretation['heterogeneity_tau2']:.4f}")
            lines.append("")

        lines.append("-" * 70)
        lines.append("SEQUENTIAL ANALYSIS")
        lines.append("-" * 70)
        lines.append(f"Efficacy boundary crossed: "
                    f"{'Yes' if self.interpretation['efficacy_crossed'] else 'No'}")
        lines.append(f"Futility boundary crossed: "
                    f"{'Yes' if self.interpretation['futility_crossed'] else 'No'}")
        lines.append("")

        lines.append("-" * 70)
        lines.append("CONCLUSION")
        lines.append("-" * 70)
        lines.append(self.interpretation['conclusion'])
        lines.append("=" * 70)

        return "\n".join(lines)

    def plot(
        self,
        show_z_curve: bool = True,
        show_boundaries: bool = True,
        show_futility: bool = True,
        figsize: tuple = (12, 8),
        **kwargs
    ):
        """
        Create TSA plot.

        Parameters
        ----------
        show_z_curve : bool
            Show cumulative Z-curve
        show_boundaries : bool
            Show monitoring boundaries
        show_futility : bool
            Show futility boundaries
        figsize : tuple
            Figure size
        **kwargs
            Additional arguments passed to plotter
        """
        plotter = TSAPlotter(self)
        return plotter.plot(
            show_z_curve=show_z_curve,
            show_boundaries=show_boundaries,
            show_futility=show_futility,
            figsize=figsize,
            **kwargs
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export results as dictionary."""
        return {
            'cumulative_results': self.cumulative_results.to_dict('records'),
            'boundaries': self.boundaries.to_dict('records'),
            'ris': self.ris,
            'alpha': self.alpha,
            'beta': self.beta,
            'effect_type': self.effect_type,
            'model_type': self.model_type,
            'interpretation': self.interpretation,
        }

    def to_dataframe(self) -> pd.DataFrame:
        """Export combined results as DataFrame."""
        return self.data.copy()
