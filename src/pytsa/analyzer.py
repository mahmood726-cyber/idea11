"""
Main TSA Analyzer class coordinating all TSA components.
"""

import numpy as np
import pandas as pd
from typing import Optional, Union, Dict, Any
from .ris import RISCalculator
from .boundaries import BoundaryFactory
from .models import ModelFactory
from .sparse_data import SparseDataHandler
from .visualization import TSAPlotter
from .results import TSAResults


class TSAAnalyzer:
    """
    Main class for performing Trial Sequential Analysis.

    Parameters
    ----------
    alpha : float, default=0.05
        Type I error rate (two-sided)
    beta : float, default=0.20
        Type II error rate (1 - power)
    effect_type : str
        Type of effect measure: 'risk_ratio', 'odds_ratio', 'risk_difference',
        'mean_difference', 'standardized_mean_difference'
    model : str, default='random_effects'
        Meta-analysis model: 'fixed_effect' or 'random_effects'
    boundary : str, default='obf'
        Monitoring boundary type: 'obf', 'lan_demets_obf', 'lan_demets_pocock', 'bonferroni'
    heterogeneity_adjustment : bool, default=True
        Apply diversity-adjusted RIS for random-effects models
    sparse_data_method : str, optional
        Method for handling sparse data: 'beta_binomial', 'continuity_correction'
    bonferroni_k : int, optional
        Number of comparisons for Bonferroni adjustment
    """

    def __init__(
        self,
        alpha: float = 0.05,
        beta: float = 0.20,
        effect_type: str = 'risk_ratio',
        model: str = 'random_effects',
        boundary: str = 'obf',
        heterogeneity_adjustment: bool = True,
        sparse_data_method: Optional[str] = None,
        bonferroni_k: Optional[int] = None
    ):
        self.alpha = alpha
        self.beta = beta
        self.effect_type = effect_type
        self.model_type = model
        self.boundary_type = boundary
        self.heterogeneity_adjustment = heterogeneity_adjustment
        self.sparse_data_method = sparse_data_method
        self.bonferroni_k = bonferroni_k

        # Adjust alpha for Bonferroni if needed
        self.adjusted_alpha = alpha / bonferroni_k if bonferroni_k else alpha

        # Initialize components
        self.ris_calculator = RISCalculator(
            alpha=self.adjusted_alpha,
            beta=beta,
            effect_type=effect_type
        )
        self.boundary = BoundaryFactory.create(
            boundary,
            alpha=self.adjusted_alpha,
            beta=beta
        )
        self.model = ModelFactory.create(model, effect_type=effect_type)

        if sparse_data_method:
            self.sparse_handler = SparseDataHandler(method=sparse_data_method)
        else:
            self.sparse_handler = None

    def fit(
        self,
        data: pd.DataFrame,
        target_effect: Optional[float] = None,
        control_event_rate: Optional[float] = None,
        variance_estimate: Optional[float] = None
    ) -> TSAResults:
        """
        Perform Trial Sequential Analysis on the provided data.

        Parameters
        ----------
        data : pd.DataFrame
            Meta-analysis data with columns depending on effect_type:
            - For dichotomous: 'events_treatment', 'n_treatment', 'events_control', 'n_control'
            - For continuous: 'mean_treatment', 'sd_treatment', 'n_treatment',
                            'mean_control', 'sd_control', 'n_control'
            Optional: 'study_id', 'year' for ordering
        target_effect : float, optional
            Target effect size (RR, OR, RD, MD, or SMD depending on effect_type)
            If None, will be estimated from data
        control_event_rate : float, optional
            Expected control group event rate (for dichotomous outcomes)
        variance_estimate : float, optional
            Variance estimate for RIS calculation

        Returns
        -------
        TSAResults
            Object containing all TSA results and visualization methods
        """
        # Handle sparse data if needed
        if self.sparse_handler:
            data = self.sparse_handler.adjust(data)

        # Perform cumulative meta-analysis
        cumulative_results = self._cumulative_meta_analysis(data)

        # Calculate RIS
        ris_params = self._prepare_ris_parameters(
            data, target_effect, control_event_rate, variance_estimate
        )
        ris = self.ris_calculator.calculate(**ris_params)

        # Apply heterogeneity adjustment if needed
        if self.heterogeneity_adjustment and self.model_type == 'random_effects':
            diversity = self._calculate_diversity(cumulative_results)
            ris = ris / (1 - diversity) if diversity < 1 else ris * 2

        # Calculate monitoring boundaries
        boundaries = self._calculate_boundaries(cumulative_results, ris)

        # Create results object
        results = TSAResults(
            cumulative_results=cumulative_results,
            ris=ris,
            boundaries=boundaries,
            alpha=self.adjusted_alpha,
            beta=self.beta,
            effect_type=self.effect_type,
            model_type=self.model_type,
            bonferroni_adjusted=self.bonferroni_k is not None
        )

        return results

    def _cumulative_meta_analysis(self, data: pd.DataFrame) -> pd.DataFrame:
        """Perform cumulative meta-analysis at each step."""
        results = []

        for i in range(1, len(data) + 1):
            subset = data.iloc[:i]
            meta_result = self.model.fit(subset)

            results.append({
                'step': i,
                'n_studies': i,
                'total_n': meta_result['total_n'],
                'effect': meta_result['effect'],
                'se': meta_result['se'],
                'variance': meta_result['variance'],
                'z_score': meta_result['z_score'],
                'p_value': meta_result['p_value'],
                'ci_lower': meta_result['ci_lower'],
                'ci_upper': meta_result['ci_upper'],
                'tau2': meta_result.get('tau2', 0),
                'I2': meta_result.get('I2', 0),
            })

        return pd.DataFrame(results)

    def _prepare_ris_parameters(
        self,
        data: pd.DataFrame,
        target_effect: Optional[float],
        control_event_rate: Optional[float],
        variance_estimate: Optional[float]
    ) -> Dict[str, Any]:
        """Prepare parameters for RIS calculation."""
        params = {}

        if target_effect is None:
            # Estimate from final meta-analysis
            final_result = self.model.fit(data)
            target_effect = final_result['effect']

        params['target_effect'] = target_effect

        if self.effect_type in ['risk_ratio', 'odds_ratio', 'risk_difference']:
            if control_event_rate is None:
                # Estimate from data
                control_event_rate = (
                    data['events_control'].sum() / data['n_control'].sum()
                )
            params['control_event_rate'] = control_event_rate

        if variance_estimate:
            params['variance'] = variance_estimate

        return params

    def _calculate_diversity(self, cumulative_results: pd.DataFrame) -> float:
        """Calculate diversity (D²) for heterogeneity adjustment."""
        final = cumulative_results.iloc[-1]
        I2 = final['I2'] / 100  # Convert percentage to proportion

        # Diversity D² = I² for most practical purposes
        # Can be refined based on specific heterogeneity model
        return I2

    def _calculate_boundaries(
        self,
        cumulative_results: pd.DataFrame,
        ris: float
    ) -> pd.DataFrame:
        """Calculate monitoring boundaries at each step."""
        information_fractions = cumulative_results['total_n'] / ris
        information_fractions = information_fractions.clip(upper=1.0)

        boundaries_data = []
        for idx, frac in enumerate(information_fractions):
            boundary_vals = self.boundary.calculate(frac, ris)
            boundaries_data.append({
                'step': idx + 1,
                'information_fraction': frac,
                'upper_boundary': boundary_vals['upper'],
                'lower_boundary': boundary_vals['lower'],
                'futility_upper': boundary_vals.get('futility_upper'),
                'futility_lower': boundary_vals.get('futility_lower'),
            })

        return pd.DataFrame(boundaries_data)
