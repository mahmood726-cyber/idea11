"""
Meta-analysis models (fixed-effect and random-effects).
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any
from abc import ABC, abstractmethod


class MetaAnalysisModel(ABC):
    """Base class for meta-analysis models."""

    def __init__(self, effect_type: str):
        self.effect_type = effect_type

    @abstractmethod
    def fit(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Fit the model to data and return results."""
        pass

    def _calculate_dichotomous_effects(self, data: pd.DataFrame) -> tuple:
        """Calculate effect sizes for dichotomous outcomes."""
        if self.effect_type == 'risk_ratio':
            return self._risk_ratio(data)
        elif self.effect_type == 'odds_ratio':
            return self._odds_ratio(data)
        elif self.effect_type == 'risk_difference':
            return self._risk_difference(data)
        else:
            raise ValueError(f"Invalid effect type for dichotomous data: {self.effect_type}")

    def _risk_ratio(self, data: pd.DataFrame) -> tuple:
        """Calculate log risk ratios and variances."""
        rt = data['events_treatment'] / data['n_treatment']
        rc = data['events_control'] / data['n_control']

        # Add small constant to avoid log(0)
        epsilon = 0.5
        rt = np.where(rt == 0, epsilon / data['n_treatment'], rt)
        rc = np.where(rc == 0, epsilon / data['n_control'], rc)

        log_rr = np.log(rt / rc)

        # Variance of log RR
        var_log_rr = (
            (1 - rt) / (data['events_treatment'] + epsilon) +
            (1 - rc) / (data['events_control'] + epsilon)
        )

        return log_rr, var_log_rr

    def _odds_ratio(self, data: pd.DataFrame) -> tuple:
        """Calculate log odds ratios and variances."""
        epsilon = 0.5

        a = data['events_treatment'] + epsilon
        b = data['n_treatment'] - data['events_treatment'] + epsilon
        c = data['events_control'] + epsilon
        d = data['n_control'] - data['events_control'] + epsilon

        log_or = np.log((a * d) / (b * c))
        var_log_or = 1/a + 1/b + 1/c + 1/d

        return log_or, var_log_or

    def _risk_difference(self, data: pd.DataFrame) -> tuple:
        """Calculate risk differences and variances."""
        rt = data['events_treatment'] / data['n_treatment']
        rc = data['events_control'] / data['n_control']

        rd = rt - rc
        var_rd = (
            rt * (1 - rt) / data['n_treatment'] +
            rc * (1 - rc) / data['n_control']
        )

        return rd, var_rd

    def _calculate_continuous_effects(self, data: pd.DataFrame) -> tuple:
        """Calculate effect sizes for continuous outcomes."""
        if self.effect_type == 'mean_difference':
            return self._mean_difference(data)
        elif self.effect_type == 'standardized_mean_difference':
            return self._standardized_mean_difference(data)
        else:
            raise ValueError(f"Invalid effect type for continuous data: {self.effect_type}")

    def _mean_difference(self, data: pd.DataFrame) -> tuple:
        """Calculate mean differences and variances."""
        md = data['mean_treatment'] - data['mean_control']

        var_md = (
            data['sd_treatment']**2 / data['n_treatment'] +
            data['sd_control']**2 / data['n_control']
        )

        return md, var_md

    def _standardized_mean_difference(self, data: pd.DataFrame) -> tuple:
        """Calculate standardized mean differences (Hedges' g) and variances."""
        # Pooled SD
        pooled_sd = np.sqrt(
            ((data['n_treatment'] - 1) * data['sd_treatment']**2 +
             (data['n_control'] - 1) * data['sd_control']**2) /
            (data['n_treatment'] + data['n_control'] - 2)
        )

        # Cohen's d
        d = (data['mean_treatment'] - data['mean_control']) / pooled_sd

        # Hedges' g correction factor
        n_total = data['n_treatment'] + data['n_control']
        j = 1 - 3 / (4 * n_total - 9)
        g = d * j

        # Variance
        var_g = (
            n_total / (data['n_treatment'] * data['n_control']) +
            g**2 / (2 * n_total)
        )

        return g, var_g


class FixedEffectModel(MetaAnalysisModel):
    """
    Fixed-effect meta-analysis using inverse-variance weighting.
    """

    def fit(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Calculate effect sizes and variances
        if 'events_treatment' in data.columns:
            effects, variances = self._calculate_dichotomous_effects(data)
            total_n = data['n_treatment'].sum() + data['n_control'].sum()
        else:
            effects, variances = self._calculate_continuous_effects(data)
            total_n = data['n_treatment'].sum() + data['n_control'].sum()

        # Inverse-variance weights
        weights = 1 / variances

        # Pooled effect
        pooled_effect = np.sum(weights * effects) / np.sum(weights)
        pooled_variance = 1 / np.sum(weights)
        pooled_se = np.sqrt(pooled_variance)

        # Z-score and p-value
        z_score = pooled_effect / pooled_se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        # Confidence interval
        z_crit = stats.norm.ppf(0.975)
        ci_lower = pooled_effect - z_crit * pooled_se
        ci_upper = pooled_effect + z_crit * pooled_se

        # Back-transform if needed
        if self.effect_type in ['risk_ratio', 'odds_ratio']:
            pooled_effect = np.exp(pooled_effect)
            ci_lower = np.exp(ci_lower)
            ci_upper = np.exp(ci_upper)

        # Heterogeneity (Q, I²)
        Q = np.sum(weights * (effects - np.sum(weights * effects) / np.sum(weights))**2)
        df = len(data) - 1
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0

        return {
            'effect': pooled_effect,
            'se': pooled_se,
            'variance': pooled_variance,
            'z_score': z_score,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'total_n': total_n,
            'Q': Q,
            'I2': I2,
            'tau2': 0  # Fixed-effect has no between-study variance
        }


class RandomEffectsModel(MetaAnalysisModel):
    """
    Random-effects meta-analysis using DerSimonian-Laird method.
    """

    def fit(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Calculate effect sizes and variances
        if 'events_treatment' in data.columns:
            effects, variances = self._calculate_dichotomous_effects(data)
            total_n = data['n_treatment'].sum() + data['n_control'].sum()
        else:
            effects, variances = self._calculate_continuous_effects(data)
            total_n = data['n_treatment'].sum() + data['n_control'].sum()

        # Inverse-variance weights (fixed-effect)
        weights_fe = 1 / variances

        # Calculate Q statistic
        mean_effect_fe = np.sum(weights_fe * effects) / np.sum(weights_fe)
        Q = np.sum(weights_fe * (effects - mean_effect_fe)**2)
        df = len(data) - 1

        # Estimate tau² (between-study variance) using DerSimonian-Laird
        C = np.sum(weights_fe) - np.sum(weights_fe**2) / np.sum(weights_fe)
        tau2 = max(0, (Q - df) / C) if C > 0 else 0

        # Random-effects weights
        weights_re = 1 / (variances + tau2)

        # Pooled effect
        pooled_effect = np.sum(weights_re * effects) / np.sum(weights_re)
        pooled_variance = 1 / np.sum(weights_re)
        pooled_se = np.sqrt(pooled_variance)

        # Z-score and p-value
        z_score = pooled_effect / pooled_se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        # Confidence interval
        z_crit = stats.norm.ppf(0.975)
        ci_lower = pooled_effect - z_crit * pooled_se
        ci_upper = pooled_effect + z_crit * pooled_se

        # I² statistic
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0

        # Back-transform if needed
        if self.effect_type in ['risk_ratio', 'odds_ratio']:
            pooled_effect = np.exp(pooled_effect)
            ci_lower = np.exp(ci_lower)
            ci_upper = np.exp(ci_upper)

        return {
            'effect': pooled_effect,
            'se': pooled_se,
            'variance': pooled_variance,
            'z_score': z_score,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'total_n': total_n,
            'Q': Q,
            'I2': I2,
            'tau2': tau2
        }


class ModelFactory:
    """Factory for creating meta-analysis models."""

    @staticmethod
    def create(model_type: str, **kwargs) -> MetaAnalysisModel:
        """Create a meta-analysis model of the specified type."""
        models = {
            'fixed_effect': FixedEffectModel,
            'random_effects': RandomEffectsModel,
        }

        if model_type not in models:
            raise ValueError(f"Unknown model type: {model_type}")

        return models[model_type](**kwargs)
