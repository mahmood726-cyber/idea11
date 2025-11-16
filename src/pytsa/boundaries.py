"""
Sequential monitoring boundary implementations.
"""

import numpy as np
from scipy import stats
from abc import ABC, abstractmethod
from typing import Dict, Any


class MonitoringBoundary(ABC):
    """Base class for monitoring boundaries."""

    def __init__(self, alpha: float = 0.05, beta: float = 0.20):
        self.alpha = alpha
        self.beta = beta
        self.z_alpha = stats.norm.ppf(1 - alpha / 2)
        self.z_beta = stats.norm.ppf(1 - beta)

    @abstractmethod
    def calculate(self, information_fraction: float, ris: float) -> Dict[str, float]:
        """Calculate boundary values at given information fraction."""
        pass


class OBrienFlemingBoundary(MonitoringBoundary):
    """
    O'Brien-Fleming boundary.

    Provides conservative early stopping boundaries that approach
    the fixed-sample z-value as information accumulates.
    """

    def calculate(self, information_fraction: float, ris: float) -> Dict[str, float]:
        if information_fraction <= 0:
            return {
                'upper': np.inf,
                'lower': -np.inf,
                'futility_upper': np.inf,
                'futility_lower': -np.inf
            }

        # O'Brien-Fleming uses sqrt(1/t) scaling
        scaling_factor = np.sqrt(1 / information_fraction)

        upper = self.z_alpha * scaling_factor
        lower = -upper

        # Futility boundaries (beta-spending)
        futility_scaling = np.sqrt(1 / information_fraction)
        futility_upper = self.z_beta * futility_scaling
        futility_lower = -futility_upper

        return {
            'upper': upper,
            'lower': lower,
            'futility_upper': futility_upper,
            'futility_lower': futility_lower
        }


class LanDeMetsOBrienFleming(MonitoringBoundary):
    """
    Lan-DeMets alpha-spending function with O'Brien-Fleming-like boundary.

    Uses alpha-spending function: alpha(t) = 2 - 2*Phi(z_alpha / sqrt(t))
    where Phi is the standard normal CDF.
    """

    def __init__(self, alpha: float = 0.05, beta: float = 0.20):
        super().__init__(alpha, beta)
        self.cumulative_alpha_spent = 0

    def calculate(self, information_fraction: float, ris: float) -> Dict[str, float]:
        if information_fraction <= 0:
            return {
                'upper': np.inf,
                'lower': -np.inf,
                'futility_upper': np.inf,
                'futility_lower': -np.inf
            }

        # Alpha-spending function (O'Brien-Fleming like)
        alpha_spent = self._alpha_spending(information_fraction)

        # Z-boundary from cumulative alpha
        z_boundary = stats.norm.ppf(1 - alpha_spent / 2)

        # Beta-spending for futility
        beta_spent = self._beta_spending(information_fraction)
        z_futility = stats.norm.ppf(1 - beta_spent)

        return {
            'upper': z_boundary,
            'lower': -z_boundary,
            'futility_upper': z_futility,
            'futility_lower': -z_futility
        }

    def _alpha_spending(self, t: float) -> float:
        """O'Brien-Fleming alpha-spending function."""
        if t >= 1:
            return self.alpha
        return 2 - 2 * stats.norm.cdf(self.z_alpha / np.sqrt(t))

    def _beta_spending(self, t: float) -> float:
        """Beta-spending function for futility."""
        if t >= 1:
            return self.beta
        return 2 - 2 * stats.norm.cdf(self.z_beta / np.sqrt(t))


class LanDemetsPocockLike(MonitoringBoundary):
    """
    Lan-DeMets alpha-spending function with Pocock-like boundary.

    Uses alpha-spending function: alpha(t) = alpha * ln(1 + (e - 1) * t)
    Provides less conservative early stopping than O'Brien-Fleming.
    """

    def calculate(self, information_fraction: float, ris: float) -> Dict[str, float]:
        if information_fraction <= 0:
            return {
                'upper': np.inf,
                'lower': -np.inf,
                'futility_upper': np.inf,
                'futility_lower': -np.inf
            }

        # Alpha-spending function (Pocock-like)
        alpha_spent = self._alpha_spending(information_fraction)

        # Z-boundary
        z_boundary = stats.norm.ppf(1 - alpha_spent / 2)

        # Beta-spending
        beta_spent = self._beta_spending(information_fraction)
        z_futility = stats.norm.ppf(1 - beta_spent)

        return {
            'upper': z_boundary,
            'lower': -z_boundary,
            'futility_upper': z_futility,
            'futility_lower': -z_futility
        }

    def _alpha_spending(self, t: float) -> float:
        """Pocock-like alpha-spending function."""
        if t >= 1:
            return self.alpha
        return self.alpha * np.log(1 + (np.e - 1) * t)

    def _beta_spending(self, t: float) -> float:
        """Beta-spending function."""
        if t >= 1:
            return self.beta
        return self.beta * np.log(1 + (np.e - 1) * t)


class BonferroniBoundary(MonitoringBoundary):
    """
    Bonferroni-adjusted boundary for multiple comparisons.

    Divides the alpha level by the number of interim analyses.
    """

    def __init__(self, alpha: float = 0.05, beta: float = 0.20, n_analyses: int = 5):
        # Adjust alpha for Bonferroni
        adjusted_alpha = alpha / n_analyses
        super().__init__(adjusted_alpha, beta)
        self.n_analyses = n_analyses

    def calculate(self, information_fraction: float, ris: float) -> Dict[str, float]:
        # Simple fixed boundaries with Bonferroni adjustment
        return {
            'upper': self.z_alpha,
            'lower': -self.z_alpha,
            'futility_upper': self.z_beta,
            'futility_lower': -self.z_beta
        }


class BoundaryFactory:
    """Factory for creating monitoring boundary objects."""

    @staticmethod
    def create(boundary_type: str, **kwargs) -> MonitoringBoundary:
        """Create a monitoring boundary of the specified type."""
        boundaries = {
            'obf': OBrienFlemingBoundary,
            'lan_demets_obf': LanDeMetsOBrienFleming,
            'lan_demets_pocock': LanDemetsPocockLike,
            'bonferroni': BonferroniBoundary,
        }

        if boundary_type not in boundaries:
            raise ValueError(f"Unknown boundary type: {boundary_type}")

        return boundaries[boundary_type](**kwargs)
