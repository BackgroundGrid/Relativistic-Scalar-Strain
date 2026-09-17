import numpy as np
from scipy.optimize import newton
from .constants import A_CRIT

def g_bar_from_g_obs(g_obs, a_crit=A_CRIT):
    """
    Computes baryonic acceleration g_bar given observed acceleration g_obs:
    g_bar = g_obs * (1 - exp(-g_obs / a_crit))
    """
    g_obs = np.asarray(g_obs)
    return g_obs * (1.0 - np.exp(-g_obs / a_crit))

def solve_g_obs(g_bar, a_crit=A_CRIT):
    """
    Inverts the non-linear constitutive law to compute g_obs from g_bar.
    Uses Newton-Raphson iteration with initial guesses tailored for both
    strong-field (planetary) and deep-strain (galactic) regimes.
    """
    g_bar_arr = np.atleast_1d(g_bar)
    g_obs_res = np.zeros_like(g_bar_arr, dtype=float)

    for idx, gb in enumerate(g_bar_arr):
        if gb <= 0:
            g_obs_res[idx] = 0.0
            continue
        
        # Initial guess: Newtonian for strong fields, sqrt(gb * a_crit) for deep strain
        x0 = gb if gb > a_crit else np.sqrt(gb * a_crit)
        
        func = lambda g: g * (1.0 - np.exp(-g / a_crit)) - gb
        fprime = lambda g: (1.0 - np.exp(-g / a_crit)) + (g / a_crit) * np.exp(-g / a_crit)
        
        g_obs_res[idx] = newton(func, x0, fprime=fprime, tol=1e-12, maxiter=100)

    return g_obs_res[0] if np.isscalar(g_bar) else g_obs_res
