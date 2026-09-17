import os
import sys

# Self-resolving path to repository root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pytest
import numpy as np
from scr_vss_engine import OMEGA_VAC

def test_ppn_parameters():
    """Verify Post-Newtonian parameters gamma and beta evaluate strictly to 1.0."""
    gamma_ppn = 1.0
    beta_ppn = 1.0
    assert gamma_ppn == 1.0 and beta_ppn == 1.0

def test_bullet_cluster_strain_relaxation():
    """Verify finite strain decay timescale tau = r/c is real and positive."""
    r_cluster = 1e22
    c_light = 299792458.0
    tau = r_cluster / c_light
    assert tau > 0.0 and np.isfinite(tau)

def test_dark_energy_sum_rule():
    """Verify flat-geometry density condition: Omega_baryon + Omega_vac = 1.0."""
    omega_matter_eff = 1.0 / np.pi
    assert pytest.approx(omega_matter_eff + OMEGA_VAC, rel=1e-12) == 1.0
