"""
Required Information Size (RIS) calculation module.
"""

import numpy as np
from scipy import stats
from typing import Optional


class RISCalculator:
    """
    Calculate Required Information Size for different effect types.

    The RIS is the total sample size or number of events needed to detect
    a target effect size with specified power and significance level.
    """

    def __init__(self, alpha: float = 0.05, beta: float = 0.20, effect_type: str = 'risk_ratio'):
        self.alpha = alpha
        self.beta = beta
        self.effect_type = effect_type

        # Calculate z-scores for two-sided test
        self.z_alpha = stats.norm.ppf(1 - alpha / 2)
        self.z_beta = stats.norm.ppf(1 - beta)

    def calculate(
        self,
        target_effect: float,
        control_event_rate: Optional[float] = None,
        variance: Optional[float] = None,
        **kwargs
    ) -> float:
        """
        Calculate RIS based on effect type.

        Parameters
        ----------
        target_effect : float
            Target effect size to detect
        control_event_rate : float, optional
            Control group event rate (for dichotomous outcomes)
        variance : float, optional
            Variance estimate (for continuous outcomes)

        Returns
        -------
        float
            Required information size (total sample size or events)
        """
        if self.effect_type == 'risk_ratio':
            return self._ris_risk_ratio(target_effect, control_event_rate)
        elif self.effect_type == 'odds_ratio':
            return self._ris_odds_ratio(target_effect, control_event_rate)
        elif self.effect_type == 'risk_difference':
            return self._ris_risk_difference(target_effect, control_event_rate)
        elif self.effect_type == 'mean_difference':
            return self._ris_mean_difference(target_effect, variance)
        elif self.effect_type == 'standardized_mean_difference':
            return self._ris_standardized_mean_difference(target_effect)
        else:
            raise ValueError(f"Unknown effect type: {self.effect_type}")

    def _ris_risk_ratio(self, rr: float, pc: float) -> float:
        """
        RIS for risk ratio (number of events needed).

        Formula from Wetterslev et al. (2008)
        """
        pt = pc * rr  # Treatment group event rate

        # Average event rate
        p_avg = (pc + pt) / 2

        # Events needed (assuming equal allocation)
        events = (
            4 * (self.z_alpha + self.z_beta) ** 2 * p_avg * (1 - p_avg)
        ) / (pc - pt) ** 2

        return events

    def _ris_odds_ratio(self, or_value: float, pc: float) -> float:
        """
        RIS for odds ratio (number of events needed).
        """
        # Convert OR to log scale for calculation
        log_or = np.log(or_value)

        # Treatment group probability from OR
        odds_c = pc / (1 - pc)
        odds_t = odds_c * or_value
        pt = odds_t / (1 + odds_t)

        # Variance of log OR
        var_log_or = 1 / (pc * (1 - pc)) + 1 / (pt * (1 - pt))

        # Events per group
        events_per_group = (
            4 * (self.z_alpha + self.z_beta) ** 2 * var_log_or
        ) / log_or ** 2

        # Total events (both groups)
        return 2 * events_per_group

    def _ris_risk_difference(self, rd: float, pc: float) -> float:
        """
        RIS for risk difference (total sample size).
        """
        pt = pc + rd

        # Sample size per group
        n_per_group = (
            2 * (self.z_alpha + self.z_beta) ** 2 *
            (pc * (1 - pc) + pt * (1 - pt))
        ) / rd ** 2

        # Total sample size
        return 2 * n_per_group

    def _ris_mean_difference(self, md: float, variance: float) -> float:
        """
        RIS for mean difference (total sample size).

        Assumes equal variance in both groups.
        """
        # Sample size per group
        n_per_group = (
            2 * variance * (self.z_alpha + self.z_beta) ** 2
        ) / md ** 2

        # Total sample size
        return 2 * n_per_group

    def _ris_standardized_mean_difference(self, smd: float) -> float:
        """
        RIS for standardized mean difference (Cohen's d).
        """
        # Sample size per group
        n_per_group = (
            2 * (self.z_alpha + self.z_beta) ** 2
        ) / smd ** 2

        # Total sample size
        return 2 * n_per_group
