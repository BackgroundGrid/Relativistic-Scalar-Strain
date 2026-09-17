import os
import sys

# Self-resolving path to repository root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pytest
import numpy as np
from scr_vss_engine import A_CRIT, OMEGA_VAC, solve_g_obs

def test_a_crit_order_of_magnitude():
    """Verify cosmic critical acceleration scale."""
    assert 1.0e-10 < A_CRIT < 1.1e-10

def test_planetary_screening_limit():
    """In strong field regimes (g_bar >> a_crit), g_obs matches g_bar precisely."""
    g_solar = 1e-2
    g_obs = solve_g_obs(g_solar)
    assert abs(g_obs - g_solar) / g_solar < 1e-12

def test_deep_strain_regime():
    """In deep strain regimes (g_bar << a_crit), g_obs approaches sqrt(g_bar * a_crit)."""
    g_bar_low = 1e-14
    g_obs = solve_g_obs(g_bar_low)
    g_expected = np.sqrt(g_bar_low * A_CRIT)
    assert abs(g_obs - g_expected) / g_expected < 1e-2

def test_horizon_dark_energy_fraction():
    """Verify asymptotic dark energy density saturation fraction equals 1 - 1/pi."""
    assert pytest.approx(OMEGA_VAC, rel=1e-5) == 0.68169
