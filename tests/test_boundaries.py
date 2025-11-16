"""
Unit tests for monitoring boundaries.
"""

import pytest
import numpy as np
from pytsa.boundaries import (
    OBrienFlemingBoundary,
    LanDeMetsOBrienFleming,
    LanDemetsPocockLike,
    BonferroniBoundary,
    BoundaryFactory
)


class TestOBrienFlemingBoundary:
    """Test O'Brien-Fleming boundary calculations."""

    def test_basic_calculation(self):
        """Test basic boundary calculation."""
        boundary = OBrienFlemingBoundary(alpha=0.05, beta=0.20)

        # At 50% information
        result = boundary.calculate(information_fraction=0.5, ris=1000)

        assert 'upper' in result
        assert 'lower' in result
        assert result['upper'] > 0
        assert result['lower'] < 0
        assert np.isclose(result['upper'], -result['lower'])

    def test_early_conservative(self):
        """Test that early boundaries are more conservative."""
        boundary = OBrienFlemingBoundary(alpha=0.05, beta=0.20)

        early = boundary.calculate(information_fraction=0.1, ris=1000)
        late = boundary.calculate(information_fraction=0.9, ris=1000)

        # Early stopping should require larger Z-score
        assert early['upper'] > late['upper']

    def test_final_analysis(self):
        """Test that final boundary approaches z_alpha."""
        boundary = OBrienFlemingBoundary(alpha=0.05, beta=0.20)

        final = boundary.calculate(information_fraction=1.0, ris=1000)

        # Should be close to 1.96 for alpha=0.05 two-sided
        assert np.isclose(final['upper'], 1.96, atol=0.01)

    def test_zero_information(self):
        """Test behavior at zero information."""
        boundary = OBrienFlemingBoundary(alpha=0.05, beta=0.20)

        result = boundary.calculate(information_fraction=0.0, ris=1000)

        # Should be infinity at zero information
        assert np.isinf(result['upper'])


class TestLanDemetsBoundaries:
    """Test Lan-DeMets spending function boundaries."""

    def test_obf_like_spending(self):
        """Test O'Brien-Fleming-like spending function."""
        boundary = LanDeMetsOBrienFleming(alpha=0.05, beta=0.20)

        result = boundary.calculate(information_fraction=0.5, ris=1000)

        assert 'upper' in result
        assert result['upper'] > 0
        assert not np.isnan(result['upper'])

    def test_pocock_like_spending(self):
        """Test Pocock-like spending function."""
        boundary = LanDemetsPocockLike(alpha=0.05, beta=0.20)

        result = boundary.calculate(information_fraction=0.5, ris=1000)

        assert 'upper' in result
        assert result['upper'] > 0

    def test_obf_vs_pocock(self):
        """Test that Pocock is less conservative early."""
        obf = LanDeMetsOBrienFleming(alpha=0.05, beta=0.20)
        pocock = LanDemetsPocockLike(alpha=0.05, beta=0.20)

        obf_result = obf.calculate(information_fraction=0.2, ris=1000)
        pocock_result = pocock.calculate(information_fraction=0.2, ris=1000)

        # Pocock should have lower (less conservative) boundary early
        assert pocock_result['upper'] < obf_result['upper']

    def test_alpha_spending_monotonic(self):
        """Test that alpha spending is monotonically increasing."""
        boundary = LanDeMetsOBrienFleming(alpha=0.05, beta=0.20)

        fractions = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        alpha_spent = []

        for frac in fractions:
            spent = boundary._alpha_spending(frac)
            alpha_spent.append(spent)

        # Alpha spending should increase with information
        assert all(alpha_spent[i] <= alpha_spent[i+1] for i in range(len(alpha_spent)-1))

        # Final alpha spent should equal alpha
        assert np.isclose(alpha_spent[-1], 0.05, atol=0.001)


class TestBonferroniBoundary:
    """Test Bonferroni-adjusted boundaries."""

    def test_bonferroni_adjustment(self):
        """Test that Bonferroni adjusts alpha correctly."""
        boundary = BonferroniBoundary(alpha=0.05, beta=0.20, n_analyses=5)

        # Adjusted alpha should be 0.05/5 = 0.01
        assert np.isclose(boundary.alpha, 0.01)

    def test_bonferroni_constant(self):
        """Test that Bonferroni boundaries are constant."""
        boundary = BonferroniBoundary(alpha=0.05, beta=0.20, n_analyses=5)

        early = boundary.calculate(information_fraction=0.2, ris=1000)
        late = boundary.calculate(information_fraction=0.8, ris=1000)

        # Should be the same (constant boundary)
        assert np.isclose(early['upper'], late['upper'])


class TestBoundaryFactory:
    """Test boundary factory."""

    def test_create_obf(self):
        """Test creating O'Brien-Fleming boundary."""
        boundary = BoundaryFactory.create('obf', alpha=0.05, beta=0.20)

        assert isinstance(boundary, OBrienFlemingBoundary)

    def test_create_lan_demets_obf(self):
        """Test creating Lan-DeMets OBF boundary."""
        boundary = BoundaryFactory.create('lan_demets_obf', alpha=0.05, beta=0.20)

        assert isinstance(boundary, LanDeMetsOBrienFleming)

    def test_create_lan_demets_pocock(self):
        """Test creating Lan-DeMets Pocock boundary."""
        boundary = BoundaryFactory.create('lan_demets_pocock', alpha=0.05, beta=0.20)

        assert isinstance(boundary, LanDemetsPocockLike)

    def test_create_bonferroni(self):
        """Test creating Bonferroni boundary."""
        boundary = BoundaryFactory.create('bonferroni', alpha=0.05, beta=0.20)

        assert isinstance(boundary, BonferroniBoundary)

    def test_invalid_type(self):
        """Test that invalid type raises error."""
        with pytest.raises(ValueError):
            BoundaryFactory.create('invalid_type', alpha=0.05, beta=0.20)


class TestBoundaryProperties:
    """Test general boundary properties."""

    def test_symmetry(self):
        """Test that upper and lower boundaries are symmetric."""
        boundaries_to_test = [
            OBrienFlemingBoundary(alpha=0.05, beta=0.20),
            LanDeMetsOBrienFleming(alpha=0.05, beta=0.20),
            LanDemetsPocockLike(alpha=0.05, beta=0.20)
        ]

        for boundary in boundaries_to_test:
            result = boundary.calculate(information_fraction=0.5, ris=1000)
            assert np.isclose(result['upper'], -result['lower'], rtol=1e-5)

    def test_information_fraction_range(self):
        """Test boundaries across full information fraction range."""
        boundary = OBrienFlemingBoundary(alpha=0.05, beta=0.20)

        fractions = np.linspace(0.1, 1.0, 10)

        for frac in fractions:
            result = boundary.calculate(information_fraction=frac, ris=1000)

            assert not np.isnan(result['upper'])
            assert not np.isnan(result['lower'])
            assert result['upper'] > 0
            assert result['lower'] < 0

    def test_futility_boundaries_present(self):
        """Test that futility boundaries are calculated."""
        boundary = OBrienFlemingBoundary(alpha=0.05, beta=0.20)

        result = boundary.calculate(information_fraction=0.5, ris=1000)

        assert 'futility_upper' in result
        assert 'futility_lower' in result

        # Futility boundaries should be inside efficacy boundaries
        assert abs(result['futility_upper']) < abs(result['upper'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
