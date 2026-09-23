#!/usr/bin/env python3
"""
===============================================================================
VACUUM STRESS SATURATION (VSS) / RELATIVISTIC SCALAR STRAIN (RSS) ARCHITECTURE
Volume 2 Mathematical Engine & Equation Solver
File: equations_results_VII.py
Output: equations_results_VII.txt (saved to current execution root)
===============================================================================
"""

import os
import sys
import numpy as np
from scipy.integrate import quad

# --- DYNAMIC OUTPUT PATH RESOLUTION ---
# Detects the directory where Run_all_VII.py is running from (current working directory)
EXECUTION_DIR = os.getcwd()
OUTPUT_TXT_PATH = os.path.join(EXECUTION_DIR, "equations_results_VII.txt")

# --- FUNDAMENTAL PHYSICAL CONSTANTS ---
c = 299792458.0                  # Speed of light (m/s)
G = 6.67430e-11                  # Gravitational constant (m^3 / kg s^2)
H0_km_s_Mpc = 67.4               # Hubble constant (km/s/Mpc)
Mpc_to_m = 3.08567758149137e22   # Meters per Megaparsec
H0_si = (H0_km_s_Mpc * 1000.0) / Mpc_to_m # H0 in s^-1

# --- VSS UNIVERSAL CONSTANTS & COSMOLOGICAL FRACTIONS ---
a_crit = (c * H0_si) / (2.0 * np.pi)  # Threshold acceleration = c*H0 / (2*pi)
Omega_b = 0.049                      # Physical Baryon density fraction
Omega_vac = 1.0 - Omega_b            # Effective Vacuum background fraction
sigma8_0 = 0.811                     # Present-day matter fluctuation amplitude

def Hubble_parameter(z):
    """Normalized expansion rate E(z) = H(z)/H0 in VSS cosmology."""
    return np.sqrt(Omega_b * (1.0 + z)**3 + Omega_vac)

def metric_slip_eta(z):
    """Analytical VSS metric slip ratio eta(z) = Phi / Psi."""
    return 1.0 - 0.116 * (1.0 + z)**(-0.38)

def integrand_growth(z_prime):
    """Integrand for linear scale-independent growth factor D(z)."""
    E = Hubble_parameter(z_prime)
    return (1.0 + z_prime) / (E**3)

def growth_factor_D(z):
    """Linear growth factor D(z) normalized to D(0) = 1."""
    I_z, _ = quad(integrand_growth, z, np.inf)
    I_0, _ = quad(integrand_growth, 0.0, np.inf)
    return (Hubble_parameter(z) * I_z) / (Hubble_parameter(0.0) * I_0)

def growth_rate_f(z, dz=0.001):
    """Growth rate f(z) = -d ln D(z) / d ln(1+z)."""
    D_plus = growth_factor_D(z + dz)
    D_minus = growth_factor_D(max(0.0, z - dz))
    dlnD_dz = (np.log(D_plus) - np.log(D_minus)) / (2.0 * dz)
    return -(1.0 + z) * dlnD_dz

def run_all_calculations():
    """Executes Volume 2 mathematical pipeline and saves output to current execution directory."""
    redshifts = [0.0, 0.5, 1.0, 2.0, 3.0, 10.0, 1089.0]
    
    lines = []
    lines.append("=" * 80)
    lines.append("VACUUM STRESS SATURATION (VSS) MONOGRAPH — VOLUME II MATHEMATICAL RESULTS")
    lines.append("=" * 80)
    lines.append(f"Hubble Constant (H0):                {H0_km_s_Mpc:.2f} km/s/Mpc")
    lines.append(f"Speed of Light (c):                  {c:.0f} m/s")
    lines.append(f"VSS Critical Acceleration (a_crit):   {a_crit:.6e} m/s^2")
    lines.append(f"Baryonic Matter Density (Omega_b):   {Omega_b:.4f}")
    lines.append(f"Effective Vacuum Density (Omega_vac): {Omega_vac:.4f}")
    lines.append(f"Normalization Amplitude (sigma_8):    {sigma8_0:.3f}")
    lines.append("-" * 80)
    lines.append("\n1. COSMOLOGICAL REDSHIFT EVOLUTION TABLE")
    lines.append("-" * 80)
    lines.append(f"{'Redshift z':<12}{'E(z)=H/H0':<14}{'Slip eta(z)':<14}{'Growth D(z)':<14}{'Rate f(z)':<14}{'f*sigma_8(z)':<14}")
    lines.append("-" * 80)
    
    for z in redshifts:
        E_z = Hubble_parameter(z)
        eta_z = metric_slip_eta(z)
        D_z = growth_factor_D(z)
        f_z = growth_rate_f(z)
        fs8_z = f_z * sigma8_0 * D_z
        lines.append(f"{z:<12.2f}{E_z:<14.5f}{eta_z:<14.5f}{D_z:<14.5f}{f_z:<14.5f}{fs8_z:<14.5f}")
        
    lines.append("-" * 80)
    lines.append("\n2. OBSERVATIONAL TENSION RESOLUTION")
    lines.append("-" * 80)
    S8_std = sigma8_0 * np.sqrt(0.3 / 0.3)
    S8_vss = sigma8_0 * np.sqrt(Omega_b / 0.3) * metric_slip_eta(0.0)
    lines.append(f"Standard GR S_8 Projection (Omega_m=0.3): {S8_std:.4f}")
    lines.append(f"VSS Metric-Slip Inferred S_8 Value:       {S8_vss:.4f}")
    lines.append(f"S_8 Suppression Ratio [eta(0) * sqrt(Omega_b/0.3)]: {S8_vss / S8_std:.4f}")
    lines.append("-" * 80)
    lines.append("END OF VOLUME II MATHEMATICAL DERIVATION REPORT")
    lines.append("=" * 80)

    content = "\n".join(lines)
    with open(OUTPUT_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"[SUCCESS] Math engine evaluated successfully. File saved to execution location:\n          {OUTPUT_TXT_PATH}")

if __name__ == "__main__":
    run_all_calculations()