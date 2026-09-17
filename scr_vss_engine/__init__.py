import sys
import os

# Self-resolving path handler
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
if ENGINE_DIR not in sys.path:
    sys.path.insert(0, ENGINE_DIR)

from .constants import C, G, H0, A_CRIT, OMEGA_VAC
from .constitutive_law import g_bar_from_g_obs, solve_g_obs

__all__ = ["C", "G", "H0", "A_CRIT", "OMEGA_VAC", "solve_g_obs", "g_bar_from_g_obs"]
