"""
Methods for handling sparse data and rare events.
"""

import numpy as np
import pandas as pd
from scipy import stats


class SparseDataHandler:
    """
    Handle sparse data and rare events in meta-analysis.

    Provides methods for:
    - Beta-binomial model for sparse dichotomous data
    - Continuity corrections for zero cells
    """

    def __init__(self, method: str = 'beta_binomial'):
        """
        Parameters
        ----------
        method : str
            Method for handling sparse data:
            - 'beta_binomial': Use beta-binomial model
            - 'continuity_correction': Add 0.5 to zero cells
        """
        self.method = method

    def adjust(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply sparse data adjustment to the data."""
        if self.method == 'beta_binomial':
            return self._beta_binomial_adjustment(data)
        elif self.method == 'continuity_correction':
            return self._continuity_correction(data)
        else:
            raise ValueError(f"Unknown sparse data method: {self.method}")

    def _continuity_correction(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply continuity correction (add 0.5 to cells with zero events).

        This is the standard approach when zero cells are present.
        """
        data = data.copy()

        # Identify studies with zero events
        zero_mask = (
            (data['events_treatment'] == 0) |
            (data['events_control'] == 0)
        )

        # Add 0.5 to all cells in studies with zero events
        if zero_mask.any():
            data.loc[zero_mask, 'events_treatment'] += 0.5
            data.loc[zero_mask, 'events_control'] += 0.5
            data.loc[zero_mask, 'n_treatment'] += 1
            data.loc[zero_mask, 'n_control'] += 1

        return data

    def _beta_binomial_adjustment(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply beta-binomial model for sparse data.

        Uses empirical Bayes approach to shrink estimates toward
        the pooled event rate, which is more appropriate for rare events.
        """
        data = data.copy()

        # Calculate pooled event rates
        total_events_t = data['events_treatment'].sum()
        total_n_t = data['n_treatment'].sum()
        total_events_c = data['events_control'].sum()
        total_n_c = data['n_control'].sum()

        pooled_rate_t = total_events_t / total_n_t if total_n_t > 0 else 0.5
        pooled_rate_c = total_events_c / total_n_c if total_n_c > 0 else 0.5

        # Estimate beta distribution parameters using method of moments
        # This provides prior information for sparse studies

        # For treatment group
        rates_t = data['events_treatment'] / data['n_treatment']
        mean_rate_t = pooled_rate_t
        var_rate_t = np.var(rates_t)

        if var_rate_t > 0 and var_rate_t < mean_rate_t * (1 - mean_rate_t):
            # Estimate alpha and beta parameters
            common_factor = mean_rate_t * (1 - mean_rate_t) / var_rate_t - 1
            alpha_t = mean_rate_t * common_factor
            beta_t = (1 - mean_rate_t) * common_factor
        else:
            # Use weak prior
            alpha_t = 1
            beta_t = 1

        # For control group
        rates_c = data['events_control'] / data['n_control']
        mean_rate_c = pooled_rate_c
        var_rate_c = np.var(rates_c)

        if var_rate_c > 0 and var_rate_c < mean_rate_c * (1 - mean_rate_c):
            common_factor = mean_rate_c * (1 - mean_rate_c) / var_rate_c - 1
            alpha_c = mean_rate_c * common_factor
            beta_c = (1 - mean_rate_c) * common_factor
        else:
            alpha_c = 1
            beta_c = 1

        # Adjust event counts using posterior means (empirical Bayes)
        data['events_treatment'] = (
            (data['events_treatment'] + alpha_t) /
            (data['n_treatment'] + alpha_t + beta_t) *
            data['n_treatment']
        )

        data['events_control'] = (
            (data['events_control'] + alpha_c) /
            (data['n_control'] + alpha_c + beta_c) *
            data['n_control']
        )

        return data


def identify_sparse_data(data: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """
    Identify studies with sparse data (event rate < threshold).

    Parameters
    ----------
    data : pd.DataFrame
        Meta-analysis data
    threshold : float
        Event rate threshold for defining sparse data

    Returns
    -------
    pd.DataFrame
        Boolean mask indicating sparse studies
    """
    rate_t = data['events_treatment'] / data['n_treatment']
    rate_c = data['events_control'] / data['n_control']

    return (rate_t < threshold) | (rate_c < threshold)
