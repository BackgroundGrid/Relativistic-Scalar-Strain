#!/usr/bin/env python3
"""
VSS/RSS Monograph Series - Volume III
Section 21: Gravitational Lensing Shear Profiles & Non-Local Vacuum Strain
File: section_21_lensing.py

Description:
  Corrected unit-pipeline script for weak gravitational lensing tangential shear.
  Executes in under 2 seconds and renders all curves in the 10^-3 to 10^-1 viewport.
"""

import numpy as np
from scipy.integrate import quad, cumulative_trapezoid
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PHYSICAL CONSTANTS & COSMOLOGICAL PARAMETERS
# ==============================================================================
M_SUN_KG = 1.98847e30          # 1 Solar Mass in kg
MPC_TO_M = 3.08567758149137e22  # 1 Mpc in meters
G_SI = 6.67430e-11             # Gravitational constant in m^3 kg^-1 s^-2
C_SI = 2.99792458e8            # Speed of light in m/s

# Monograph Acceleration Gate Scale
A_CRIT = 1.042e-10             # a_crit = c * H_0 / (2 * pi) in m/s^2

# Cluster Parameters
M_TOT_BAR_MSUN = 1.5e14        # Total baryonic mass in M_sun
R_CORE_MPC = 0.10              # Core radius in Mpc
R_200_MPC = 1.80               # Cosmological screening boundary in Mpc

# Lensing Geometry (z_l = 0.2, z_s = 0.8)
D_L_MPC = 620.0
D_S_MPC = 1800.0
D_LS_MPC = 1350.0

# Convert distances to SI meters
D_l_m = D_L_MPC * MPC_TO_M
D_s_m = D_S_MPC * MPC_TO_M
D_ls_m = D_LS_MPC * MPC_TO_M

# Critical Surface Mass Density (M_sun / Mpc^2)
Sigma_crit_SI = (C_SI**2 / (4.0 * np.pi * G_SI)) * (D_s_m / (D_l_m * D_ls_m))
SIGMA_CRIT_MSUN_MPC2 = Sigma_crit_SI * (MPC_TO_M**2 / M_SUN_KG)

# ==============================================================================
# 2. DENSITY PROFILES
# ==============================================================================
def M_bar_Msun(r_mpc):
    return M_TOT_BAR_MSUN * (r_mpc**2) / ((r_mpc + R_CORE_MPC)**2)

def g_N_si(r_mpc):
    r_m = r_mpc * MPC_TO_M
    m_kg = M_bar_Msun(r_mpc) * M_SUN_KG
    return (G_SI * m_kg) / (r_m**2)

def nu_vss(y):
    return 0.5 + 0.5 * np.sqrt(1.0 + 4.0 / y)

def nu_screened(r_mpc):
    g_val = g_N_si(r_mpc)
    y_val = g_val / A_CRIT
    nu_raw = nu_vss(y_val)
    screening = 1.0 / (1.0 + (r_mpc / R_200_MPC)**2)
    return 1.0 + (nu_raw - 1.0) * screening

def M_eff_vss_Msun(r_mpc):
    return M_bar_Msun(r_mpc) * nu_screened(r_mpc)

def rho_bar_Msun_Mpc3(r_mpc):
    dM_dr = M_TOT_BAR_MSUN * (2.0 * r_mpc * R_CORE_MPC) / ((r_mpc + R_CORE_MPC)**3)
    return dM_dr / (4.0 * np.pi * r_mpc**2)

def rho_eff_vss_Msun_Mpc3(r_mpc):
    dr = 1e-4 * r_mpc
    dM_dr = (M_eff_vss_Msun(r_mpc + dr) - M_eff_vss_Msun(r_mpc - dr)) / (2.0 * dr)
    return dM_dr / (4.0 * np.pi * r_mpc**2)

def rho_nfw_Msun_Mpc3(r_mpc):
    M_200 = 8.0e14
    c_nfw = 4.0
    r_s = R_200_MPC / c_nfw
    x = r_mpc / r_s
    rho_0 = (M_200 / (4.0 * np.pi * r_s**3)) / (np.log(1.0 + c_nfw) - c_nfw / (1.0 + c_nfw))
    return rho_0 / (x * (1.0 + x)**2)

# ==============================================================================
# 3. VECTORIZED SURFACE DENSITY & SHEAR PIPELINE
# ==============================================================================
def compute_shear_profile(rho_func, R_target):
    r_grid = np.logspace(-3, 1.0, 300)
    Sigma_grid = np.zeros_like(r_grid)

    for i, R_val in enumerate(r_grid):
        def integrand(u):
            return rho_func(np.sqrt(R_val**2 + u**2))
        Sigma_grid[i], _ = quad(integrand, 0.0, 20.0, limit=100)
    Sigma_grid *= 2.0

    integrand_encl = Sigma_grid * r_grid
    integral_val = cumulative_trapezoid(integrand_encl, r_grid, initial=0.0)
    
    bar_Sigma_grid = np.zeros_like(r_grid)
    bar_Sigma_grid[1:] = (2.0 / (r_grid[1:]**2)) * integral_val[1:]
    bar_Sigma_grid[0] = Sigma_grid[0]

    f_Sigma = interp1d(r_grid, Sigma_grid, kind='cubic')
    f_bar_Sigma = interp1d(r_grid, bar_Sigma_grid, kind='cubic')

    Sigma_target = f_Sigma(R_target)
    bar_Sigma_target = f_bar_Sigma(R_target)

    gamma_t = (bar_Sigma_target - Sigma_target) / SIGMA_CRIT_MSUN_MPC2
    return gamma_t

# ==============================================================================
# 4. EXECUTION & VISUAL GENERATION
# ==============================================================================
if __name__ == "__main__":
    R_grid = np.logspace(-1, 0.7, 50) # 0.1 Mpc to 5.0 Mpc
    
    shear_gr = compute_shear_profile(rho_bar_Msun_Mpc3, R_grid)
    shear_nfw = compute_shear_profile(rho_nfw_Msun_Mpc3, R_grid)
    shear_vss = compute_shear_profile(rho_eff_vss_Msun_Mpc3, R_grid)
    boost_grid = [nu_screened(r) for r in R_grid]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    ax1.loglog(R_grid, shear_vss, 'b-', lw=2.5, label='Screened VSS (Pure Baryons)')
    ax1.loglog(R_grid, shear_nfw, 'k--', lw=2.0, label=r'$\Lambda$CDM NFW DM Benchmark')
    ax1.loglog(R_grid, shear_gr, 'r:', lw=2.0, label='Pure GR (Baryons Only)')
    ax1.set_xlabel('Projected Radius $R$ [Mpc]', fontsize=12)
    ax1.set_ylabel(r'Tangential Lensing Shear $\gamma_t(R)$', fontsize=12)
    ax1.set_title('Cluster Lensing Shear Comparison', fontsize=13, fontweight='bold')
    ax1.set_ylim(1e-4, 0.2) 
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend(fontsize=10)

    ax2.semilogx(R_grid, boost_grid, 'm-', lw=2.5, label=r'Acceleration Boost $g_{\mathrm{eff}} / g_N$')
    ax2.axvline(R_200_MPC, color='gray', linestyle='--', label=r'Screening Boundary $R_{200}$')
    ax2.set_xlabel('Physical Radius $r$ [Mpc]', fontsize=12)
    ax2.set_ylabel(r'Acceleration Ratio $g_{\mathrm{eff}} / g_N$', fontsize=12)
    ax2.set_title('VSS Non-Local Strain Boost Profile', fontsize=13, fontweight='bold')
    ax2.grid(True, which="both", ls="--", alpha=0.5)
    ax2.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('section_21_lensing_profiles.png')
    print("Re-rendered figure saved to 'section_21_lensing_profiles.png'")