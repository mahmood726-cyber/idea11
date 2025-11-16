"""
Unit tests for Required Information Size (RIS) calculations.
"""

import pytest
import numpy as np
from pytsa.ris import RISCalculator


class TestRISCalculator:
    """Test RIS calculations for different effect types."""

    def test_risk_ratio_ris(self):
        """Test RIS calculation for risk ratio."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')

        # Test case: RR = 0.75, control rate = 20%
        ris = calc.calculate(target_effect=0.75, control_event_rate=0.20)

        # RIS should be reasonable (between 100 and 10000 events typically)
        assert 100 < ris < 10000

        # RIS should increase with smaller effect sizes
        ris_small = calc.calculate(target_effect=0.90, control_event_rate=0.20)
        assert ris_small > ris

    def test_odds_ratio_ris(self):
        """Test RIS calculation for odds ratio."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='odds_ratio')

        ris = calc.calculate(target_effect=0.70, control_event_rate=0.20)

        assert 100 < ris < 10000
        assert not np.isnan(ris)
        assert not np.isinf(ris)

    def test_risk_difference_ris(self):
        """Test RIS calculation for risk difference."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_difference')

        # RD = -0.05 (5% absolute reduction), control rate = 20%
        ris = calc.calculate(target_effect=-0.05, control_event_rate=0.20)

        assert 100 < ris < 50000  # Total sample size
        assert not np.isnan(ris)

    def test_mean_difference_ris(self):
        """Test RIS calculation for mean difference."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='mean_difference')

        # MD = -5, variance = 100
        ris = calc.calculate(target_effect=-5.0, variance=100.0)

        assert 10 < ris < 10000
        assert not np.isnan(ris)

    def test_standardized_mean_difference_ris(self):
        """Test RIS calculation for SMD."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='standardized_mean_difference')

        # Cohen's d = 0.5 (medium effect)
        ris = calc.calculate(target_effect=0.5)

        assert 50 < ris < 1000
        assert not np.isnan(ris)

        # Smaller effect should require larger sample size
        ris_small = calc.calculate(target_effect=0.2)  # Small effect
        assert ris_small > ris

    def test_alpha_beta_effect(self):
        """Test that changing alpha/beta affects RIS appropriately."""
        # Lower alpha (more stringent) should increase RIS
        calc_005 = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')
        calc_001 = RISCalculator(alpha=0.01, beta=0.20, effect_type='risk_ratio')

        ris_005 = calc_005.calculate(target_effect=0.75, control_event_rate=0.20)
        ris_001 = calc_001.calculate(target_effect=0.75, control_event_rate=0.20)

        assert ris_001 > ris_005

        # Lower beta (higher power) should increase RIS
        calc_beta20 = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')
        calc_beta10 = RISCalculator(alpha=0.05, beta=0.10, effect_type='risk_ratio')

        ris_beta20 = calc_beta20.calculate(target_effect=0.75, control_event_rate=0.20)
        ris_beta10 = calc_beta10.calculate(target_effect=0.75, control_event_rate=0.20)

        assert ris_beta10 > ris_beta20

    def test_extreme_event_rates(self):
        """Test RIS with extreme event rates."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')

        # Very low event rate
        ris_low = calc.calculate(target_effect=0.50, control_event_rate=0.01)
        assert not np.isnan(ris_low)
        assert ris_low > 0

        # Moderate event rate
        ris_mod = calc.calculate(target_effect=0.50, control_event_rate=0.20)

        # RIS should be smaller for higher event rates (less variance)
        assert ris_low > ris_mod

    def test_invalid_effect_type(self):
        """Test that invalid effect type raises error."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='invalid_type')

        with pytest.raises(ValueError):
            calc.calculate(target_effect=0.75)

    def test_ris_positive(self):
        """Test that RIS is always positive."""
        effect_types = ['risk_ratio', 'odds_ratio', 'risk_difference',
                       'mean_difference', 'standardized_mean_difference']

        for effect_type in effect_types:
            calc = RISCalculator(alpha=0.05, beta=0.20, effect_type=effect_type)

            if effect_type in ['risk_ratio', 'odds_ratio']:
                ris = calc.calculate(target_effect=0.75, control_event_rate=0.20)
            elif effect_type == 'risk_difference':
                ris = calc.calculate(target_effect=-0.05, control_event_rate=0.20)
            elif effect_type == 'mean_difference':
                ris = calc.calculate(target_effect=-5.0, variance=100.0)
            else:  # SMD
                ris = calc.calculate(target_effect=0.5)

            assert ris > 0, f"RIS should be positive for {effect_type}"


class TestRISEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_null_effect(self):
        """Test RIS with null effect (should be very large or infinite)."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')

        # RR = 1.0 (no effect) should require very large or infinite sample size
        # In practice, this should either be very large or raise an error
        # For now, we just check it doesn't crash
        try:
            ris = calc.calculate(target_effect=1.0, control_event_rate=0.20)
            # If it doesn't error, RIS should be very large
            assert ris > 100000 or np.isinf(ris)
        except (ValueError, ZeroDivisionError):
            # It's also acceptable to raise an error for null effect
            pass

    def test_very_large_effect(self):
        """Test RIS with very large effect size."""
        calc = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')

        # Very large effect (RR = 0.1) should require small sample size
        ris = calc.calculate(target_effect=0.10, control_event_rate=0.20)

        assert ris > 0
        assert ris < 1000  # Should be relatively small

    def test_consistency_across_calculators(self):
        """Test that creating new calculator gives same results."""
        calc1 = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')
        calc2 = RISCalculator(alpha=0.05, beta=0.20, effect_type='risk_ratio')

        ris1 = calc1.calculate(target_effect=0.75, control_event_rate=0.20)
        ris2 = calc2.calculate(target_effect=0.75, control_event_rate=0.20)

        assert np.isclose(ris1, ris2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
