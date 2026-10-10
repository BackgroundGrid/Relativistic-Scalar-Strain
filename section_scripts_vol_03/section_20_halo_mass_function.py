"""
Relativistic Scalar Strain (RSS) Architecture - Volume III
Section 20: Halo Mass Function & Cosmological Cluster Abundance Engine
Copyright (C) 2026 Ravinder Singh. All Rights Reserved.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# PHYSICAL CONSTANTS & FIRST-PRINCIPLES NUMERICAL EVALUATION
# ==============================================================================
C_SI = 2.99792458e8                            # Speed of light (m/s)
H0_KM_S_MPC = 67.4                             # Hubble parameter (km/s/Mpc)
H_LITTLE = H0_KM_S_MPC / 100.0                 # Dimensionless Hubble parameter h = 0.674
MPC_TO_METERS = 3.08567758149137e22            # Meters per Megaparsec
OMEGA_M_0 = 0.315                              # Matter density parameter
RHO_CRIT_0 = 2.77536627e11                     # Critical density in h^2 M_sun / Mpc^3
RHO_BAR_0 = OMEGA_M_0 * RHO_CRIT_0             # Mean comoving matter density

# Classical Einstein-de Sitter Spherical Top-Hat Collapse Barrier
DELTA_C_0 = (3.0 * (12.0 * np.pi)**(2.0 / 3.0)) / 20.0  # ~1.68647

# Action-Derived Transition Scale & Vacuum Parameters
K_H_SI = (H0_KM_S_MPC * 1000.0 / MPC_TO_METERS) / C_SI
K_H_H_MPC = (K_H_SI * MPC_TO_METERS) / H_LITTLE
K_TRANS = (2.0 * np.pi)**3 * np.sqrt(2.0 * np.pi) * K_H_H_MPC  # ~0.2074 h/Mpc
GAMMA_DEFAULT = 1.5
MU_0 = 0.116
ALPHA_EXPONENT = 0.38

# Variance & Sheth-Tormen Parameters
SIGMA_8 = 0.811
ST_A = 0.3222
ST_Q = 0.7070
ST_P = 0.3000


# ==============================================================================
# CORE FORMULATIONS & MASS FUNCTION CALCULATIONS
# ==============================================================================
def mass_to_wavenumber(mass_h_msun):
    """Maps halo mass M [h^-1 M_sun] to spatial wavenumber k [h/Mpc]."""
    radius_mpc_h = (3.0 * mass_h_msun / (4.0 * np.pi * RHO_BAR_0))**(1.0 / 3.0)
    wavenumber_k = (2.0 * np.pi) / radius_mpc_h
    return wavenumber_k, radius_mpc_h


def linear_growth_factor(z):
    """Approximates normalized linear growth factor D(z) for Omega_m = 0.315."""
    omega_m_z = OMEGA_M_0 * (1.0 + z)**3 / (OMEGA_M_0 * (1.0 + z)**3 + (1.0 - OMEGA_M_0))
    d_z = (5.0 / 2.0) * omega_m_z / (
        omega_m_z**(4.0 / 7.0) - (1.0 - omega_m_z) + (1.0 + omega_m_z / 2.0) * (1.0 + (1.0 - omega_m_z) / 70.0)
    )
    d_0 = (5.0 / 2.0) * OMEGA_M_0 / (
        OMEGA_M_0**(4.0 / 7.0) - (1.0 - OMEGA_M_0) + (1.0 + OMEGA_M_0 / 2.0) * (1.0 + (1.0 - OMEGA_M_0) / 70.0)
    )
    return (d_z / d_0) / (1.0 + z)


def sigma_mass(mass_h_msun, z=0.0):
    """
    Computes RMS linear mass variance sigma(M, z) using power-law index gamma_s = 0.155,
    normalized to sigma_8 at R = 8 h^-1 Mpc.
    """
    _, r_mpc_h = mass_to_wavenumber(mass_h_msun)
    r_8 = 8.0
    sigma_z0 = SIGMA_8 * (r_8 / r_mpc_h)**(3.0 * 0.155)
    return sigma_z0 * linear_growth_factor(z)


def dln_sigma_dln_m(mass_h_msun):
    """Logarithmic slope |d ln sigma / d ln M| = 0.155."""
    return 0.155


def scalar_field_propagator(k, k_trans=K_TRANS, gamma=GAMMA_DEFAULT):
    """Tree-level non-local field propagator S(k)."""
    k_arr = np.asarray(k, dtype=np.float64)
    return 1.0 / (1.0 + (k_arr / k_trans)**gamma)


def spherical_collapse_threshold(mass_h_msun, z):
    """Scale- and redshift-dependent linear collapse threshold delta_c(z, M)."""
    k, _ = mass_to_wavenumber(mass_h_msun)
    s_k = scalar_field_propagator(k)
    strain_suppression = (MU_0 / 3.0) * ((1.0 + z)**(-ALPHA_EXPONENT)) * s_k
    return DELTA_C_0 * (1.0 - strain_suppression)


def sheth_tormen_f_nu(nu):
    """Sheth-Tormen multiplicity function f(nu)."""
    nu_arr = np.asarray(nu, dtype=np.float64)
    term1 = ST_A * np.sqrt(2.0 * ST_Q / np.pi)
    term2 = 1.0 + (ST_Q * (nu_arr**2))**(-ST_P)
    term3 = nu_arr * np.exp(-0.5 * ST_Q * (nu_arr**2))
    return term1 * term2 * term3


def differential_hmf(mass_h_msun, z, use_vss=True):
    """
    Calculates differential halo mass function dn/dlnM [h^3 Mpc^-3].
    If use_vss=True, applies scale-dependent delta_c(z, M).
    If use_vss=False, uses classical GR constant barrier delta_c = 1.68647.
    """
    sig = sigma_mass(mass_h_msun, z)
    if use_vss:
        delta_c = spherical_collapse_threshold(mass_h_msun, z)
    else:
        delta_c = DELTA_C_0

    nu = delta_c / sig
    f_nu = sheth_tormen_f_nu(nu)
    dln_sig = dln_sigma_dln_m(mass_h_msun)

    dn_dlnm = (RHO_BAR_0 / mass_h_msun) * f_nu * dln_sig
    return dn_dlnm


# ==============================================================================
# VISUALIZATION ENGINE (SAVING DIRECTLY TO EXECUTION FOLDER)
# ==============================================================================
def generate_visuals(mass_array, z_list, output_filename="figure_20_1_halo_mass_function.png"):
    """Generates dual-panel publication graphic matching Vol 1 & 2 pathing convention."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8), dpi=300)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # OVERALL FIGURE TITLE FOR MONOGRAPH
    fig.suptitle(
        r"Figure 20.1: Modified Differential Halo Mass Function $dn/d\ln M$ and High-Redshift Abundance Boost",
        fontsize=14,
        fontweight='bold',
        y=0.98
    )

    # Panel 1: Differential Halo Mass Function dn/dlnM
    for z, color in zip(z_list, colors):
        hmf_vss = [differential_hmf(m, z, use_vss=True) for m in mass_array]
        hmf_gr = [differential_hmf(m, z, use_vss=False) for m in mass_array]

        ax1.loglog(mass_array, hmf_vss, label=f'VSS z = {z:.1f}', color=color, lw=2.2)
        ax1.loglog(mass_array, hmf_gr, linestyle='--', color=color, lw=1.2, alpha=0.7)

    ax1.set_xlabel(r'Halo Mass $M \; [h^{-1} M_\odot]$', fontsize=11)
    ax1.set_ylabel(r'$dn / d\ln M \; [h^3 \, \mathrm{Mpc}^{-3}]$', fontsize=11)
    ax1.set_title(r'Differential Halo Mass Function $dn/d\ln M$', fontsize=12, fontweight='bold')
    ax1.grid(True, which="both", ls="--", alpha=0.35)
    ax1.legend(loc='lower left', frameon=True, fontsize=9)

    # Panel 2: Abundance Ratio VSS / GR
    for z, color in zip(z_list, colors):
        hmf_vss = np.array([differential_hmf(m, z, use_vss=True) for m in mass_array])
        hmf_gr = np.array([differential_hmf(m, z, use_vss=False) for m in mass_array])
        ratio = hmf_vss / hmf_gr

        ax2.semilogx(mass_array, ratio, label=f'z = {z:.1f}', color=color, lw=2.2)

    ax2.axhline(1.0, color='black', linestyle='--', alpha=0.7, label='GR Baseline (1.00)')
    ax2.set_xlabel(r'Halo Mass $M \; [h^{-1} M_\odot]$', fontsize=11)
    ax2.set_ylabel(r'Abundance Ratio $(dn/d\ln M)_{\mathrm{VSS}} / (dn/d\ln M)_{\mathrm{GR}}$', fontsize=11)
    ax2.set_title(r'Cluster Abundance Enhancement Ratio', fontsize=12, fontweight='bold')
    ax2.grid(True, which="both", ls="--", alpha=0.35)
    ax2.legend(loc='upper left', frameon=True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    return output_filename


# ==============================================================================
# MAIN SECTION EXECUTOR (LIVE TERMINAL OUTPUT & STRUCTURED DATA RETURN)
# ==============================================================================
def run_section_20():
    """Executes Section 20 calculations, logs to screen, and outputs figures to execution folder."""
    
    print("=" * 84)
    print(" VSS/RSS MONOGRAPH SERIES - VOLUME III: SECTION 20")
    print(" Halo Mass Function & Cosmological Cluster Abundance Engine")
    print("=" * 84)
    
    print("\n[1] COSMOLOGICAL CONSTANTS & HMF CONSTANTS:")
    print(f"  * Mean Comoving Matter Density (rho_bar_0): {RHO_BAR_0:.4e} h^2 M_sun/Mpc^3")
    print(f"  * Linear Variance Normalization (sigma_8): {SIGMA_8:.3f}")
    print(f"  * Sheth-Tormen Parameters                  : A={ST_A:.4f}, q={ST_Q:.4f}, p={ST_P:.4f}")
    print(f"  * Action Cutoff Scale (k_trans)            : {K_TRANS:.6f} h/Mpc")

    mass_test_list = [1e15, 1e14, 1e13, 1e12, 1e10]
    redshifts = [0.0, 1.0, 2.0]
    
    print("\n[2] NUMERICAL EVALUATION OF HMF ENHANCEMENT MATRIX:")
    print("-" * 84)
    print(f"{'Mass [h^-1 M_sun]':^18} | {'z':^5} | {'HMF (GR)':^15} | {'HMF (VSS)':^15} | {'Ratio (VSS/GR)':^15}")
    print("-" * 84)

    results_table = []
    for m in mass_test_list:
        for z in redshifts:
            hmf_gr = differential_hmf(m, z, use_vss=False)
            hmf_vss = differential_hmf(m, z, use_vss=True)
            ratio = hmf_vss / hmf_gr
            
            results_table.append({
                'mass': m,
                'z': z,
                'hmf_gr': hmf_gr,
                'hmf_vss': hmf_vss,
                'ratio': ratio
            })
            
            print(f"{m:^18.1e} | {z:^5.1f} | {hmf_gr:^15.4e} | {hmf_vss:^15.4e} | {ratio:^15.4f}")

    print("-" * 84)

    # Generate figure in execution folder
    mass_array = np.logspace(10, 15, 300)
    z_fig_list = [0.0, 0.5, 1.0, 2.0]
    fig_filename = "figure_20_1_halo_mass_function.png"
    fig_path = generate_visuals(mass_array, z_fig_list, output_filename=fig_filename)
    
    print("\n[3] VISUAL GRAPHIC ASSET GENERATED:")
    print(f"  * Rendered Figure Asset -> {os.path.abspath(fig_path)}")

    sec20_data_payload = {
        'section_id': 20,
        'title': 'Halo Mass Function & Cosmological Cluster Abundance Engine',
        'k_trans': K_TRANS,
        'sigma_8': SIGMA_8,
        'table': results_table,
        'figure_path': os.path.abspath(fig_path)
    }

    print("\n[Section 20 Execution Complete]\n")
    return sec20_data_payload


if __name__ == "__main__":
    run_section_20()