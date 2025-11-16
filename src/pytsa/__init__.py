"""
PyTSA: Python Trial Sequential Analysis Platform

A comprehensive implementation of Trial Sequential Analysis for meta-analysis.
"""

from .analyzer import TSAAnalyzer
from .boundaries import (
    OBrienFlemingBoundary,
    LanDeMetsOBrienFleming,
    LanDemetsPocockLike,
    BonferroniBoundary
)
from .ris import RISCalculator
from .models import FixedEffectModel, RandomEffectsModel

__version__ = "0.1.0"
__all__ = [
    "TSAAnalyzer",
    "OBrienFlemingBoundary",
    "LanDeMetsOBrienFleming",
    "LanDemetsPocockLike",
    "BonferroniBoundary",
    "RISCalculator",
    "FixedEffectModel",
    "RandomEffectsModel",
]
