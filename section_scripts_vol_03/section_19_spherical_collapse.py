"""
Relativistic Scalar Strain (RSS) Architecture - Volume III
Section 19: Spherical & Ellipsoidal Halo Collapse Engine delta_c(z, M)
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
RHO_CRIT_0 = 2.77536627e11                     # Critical density in h^2 M_sun / Mpc^3

# Classical Einstein-de Sitter Spherical Top-Hat Collapse Barrier
DELTA_C_0 = (3.0 * (12.0 * np.pi)**(2.0 / 3.0)) / 20.0  # ~1.68647

# Hubble parameter in SI units (1/s)
H0_SI = (H0_KM_S_MPC * 1000.0) / MPC_TO_METERS  # ~2.18432e-18 s^-1

# Axiomatic Vacuum Elasticity Acceleration Scale
A_CRIT = (C_SI * H0_SI) / (2.0 * np.pi)         # ~1.04217e-10 m/s^2

# Fundamental Horizon Wavenumber k_H
K_H_SI = H0_SI / C_SI                          # ~7.28611e-27 m^-1
K_H_MPC = K_H_SI * MPC_TO_METERS               # ~2.24826e-4 Mpc^-1
K_H_H_MPC = K_H_MPC / H_LITTLE                 # ~3.3357e-4 h/Mpc

# Action-Derived Transition Scale k_trans = (2pi)^3 * sqrt(2pi) * k_H
K_TRANS = (2.0 * np.pi)**3 * np.sqrt(2.0 * np.pi) * K_H_H_MPC  # ~0.2074 h/Mpc
GAMMA_DEFAULT = 1.5                            # Propagator kinetic exponent
MU_0 = 0.116                                   # Vacuum strain amplitude (Volume II)
ALPHA_EXPONENT = 0.38                          # Temporal strain decay exponent


# ==============================================================================
# CORE FORMULATIONS & COLLAPSE THRESHOLDS
# ==============================================================================
def mass_to_wavenumber(mass_h_msun, omega_m=0.315):
    """
    Maps halo mass M [h^-1 M_sun] to spatial wavenumber k [h/Mpc]
    via comoving top-hat radius R(M) = [3M / (4*pi*rho_bar)]^(1/3).
    """
    rho_bar = omega_m * RHO_CRIT_0  # Comoving matter density in h^2 M_sun / Mpc^3
    radius_mpc_h = (3.0 * mass_h_msun / (4.0 * np.pi * rho_bar))**(1.0 / 3.0)
    wavenumber_k = (2.0 * np.pi) / radius_mpc_h
    return wavenumber_k, radius_mpc_h


def scalar_field_propagator(k, k_trans=K_TRANS, gamma=GAMMA_DEFAULT):
    """Tree-level Green's function factor S(k) from non-local action."""
    k_arr = np.asarray(k, dtype=np.float64)
    return 1.0 / (1.0 + (k_arr / k_trans)**gamma)


def spherical_collapse_threshold(mass_h_msun, z, k_trans=K_TRANS, gamma=GAMMA_DEFAULT):
    """
    Scale- and redshift-dependent linear spherical collapse threshold delta_c(z, M):
    delta_c(z, M) = delta_c^(0) * [ 1 - (mu_0 / 3) * (1 + z)^(-alpha) * S(k(M)) ]
    """
    k, _ = mass_to_wavenumber(mass_h_msun)
    s_k = scalar_field_propagator(k, k_trans, gamma)
    strain_suppression = (MU_0 / 3.0) * ((1.0 + z)**(-ALPHA_EXPONENT)) * s_k
    return DELTA_C_0 * (1.0 - strain_suppression)


def ellipsoidal_collapse_threshold(delta_c_val, nu, e=0.15, p=0.05):
    """
    Sheth-Tormen Ellipsoidal collapse threshold delta_c,ellip(nu, e, p):
    delta_c,ellip = delta_c * [ 1 + 0.47 * (5 * (e^2 - p^2) * nu^2)^0.615 ]
    """
    nu_arr = np.asarray(nu, dtype=np.float64)
    shear_factor = 5.0 * (e**2 - p**2) * (nu_arr**2)
    shear_factor = np.maximum(shear_factor, 1e-10)  # Avoid zero-power warnings
    return delta_c_val * (1.0 + 0.47 * (shear_factor**0.615))


# ==============================================================================
# VISUALIZATION ENGINE (SAVING DIRECTLY TO EXECUTION FOLDER)
# ==============================================================================
def generate_visuals(mass_array, z_list, output_filename="figure_19_1_spherical_collapse.png"):
    """Generates dual-panel publication graphic matching Vol 1 & 2 pathing convention."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8), dpi=300)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # OVERALL FIGURE TITLE FOR MONOGRAPH
    fig.suptitle(
        r"Figure 19.1: Scale-Dependent Spherical Collapse Threshold $\delta_c(z, M)$ and Ellipsoidal Collapse Surfaces",
        fontsize=14,
        fontweight='bold',
        y=0.98
    )

    # Panel 1: Spherical Collapse Threshold vs Halo Mass
    for z, color in zip(z_list, colors):
        delta_c_vals = [spherical_collapse_threshold(m, z) for m in mass_array]
        ax1.semilogx(mass_array, delta_c_vals, label=f'z = {z:.1f}', color=color, lw=2.2)

    ax1.axhline(DELTA_C_0, color='black', linestyle='--', alpha=0.7,
                label=rf'GR Top-Hat Limit $\delta_c^{{(0)}} = {DELTA_C_0:.5f}$')
    ax1.set_xlabel(r'Halo Mass $M \; [h^{-1} M_\odot]$', fontsize=11)
    ax1.set_ylabel(r'Linear Collapse Threshold $\delta_c(z, M)$', fontsize=11)
    ax1.set_title(r'VSS Modified Spherical Collapse Barrier', fontsize=12, fontweight='bold')
    ax1.grid(True, which="both", ls="--", alpha=0.35)
    ax1.legend(loc='lower right', frameon=True)

    # Panel 2: Ellipsoidal Collapse Barrier vs Peak Height nu
    nu_array = np.linspace(0.5, 3.5, 200)
    ellipticities = [0.05, 0.15, 0.25]
    line_styles = ['-', '--', '-.']

    delta_c_z0_mw = spherical_collapse_threshold(1e13, 0.0)  # Milky Way scale reference

    for e_val, ls in zip(ellipticities, line_styles):
        delta_ellip = ellipsoidal_collapse_threshold(delta_c_z0_mw, nu_array, e=e_val, p=e_val / 3.0)
        ax2.plot(nu_array, delta_ellip, label=f'Ellipticity $e = {e_val:.2f}$', color='#1f77b4', linestyle=ls, lw=2.0)

    delta_ellip_gr = ellipsoidal_collapse_threshold(DELTA_C_0, nu_array, e=0.15, p=0.05)
    ax2.plot(nu_array, delta_ellip_gr, label=r'Standard GR Ellipsoidal ($e=0.15$)', color='black', linestyle=':', lw=2.2)

    ax2.set_xlabel(r'Peak Height Parameter $\nu \equiv \delta_c / \sigma(M)$', fontsize=11)
    ax2.set_ylabel(r'Ellipsoidal Threshold $\delta_{c,\mathrm{ellip}}$', fontsize=11)
    ax2.set_title(r'Sheth-Tormen Ellipsoidal Collapse Surfaces', fontsize=12, fontweight='bold')
    ax2.grid(True, which="both", ls="--", alpha=0.35)
    ax2.legend(loc='upper left', frameon=True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    return output_filename


# ==============================================================================
# MAIN SECTION EXECUTOR (LIVE TERMINAL OUTPUT & STRUCTURED DATA RETURN)
# ==============================================================================
def run_section_19():
    """Executes Section 19 calculations, logs to screen, and outputs figures to execution folder."""
    
    print("=" * 84)
    print(" VSS/RSS MONOGRAPH SERIES - VOLUME III: SECTION 19")
    print(" Spherical & Ellipsoidal Halo Collapse Engine delta_c(z, M)")
    print("=" * 84)
    
    print("\n[1] ACTION DERIVATION & FIRST-PRINCIPLES CONSTANTS:")
    print(f"  * Speed of Light (c)               : {C_SI:.8e} m/s")
    print(f"  * Hubble Parameter (H0)            : {H0_KM_S_MPC:.2f} km/s/Mpc ({H0_SI:.6e} s^-1)")
    print(f"  * Axiomatic Acceleration (a_crit)  : {A_CRIT:.6e} m/s^2")
    print(f"  * GR Top-Hat Collapse Threshold    : {DELTA_C_0:.6f}")
    print(f"  * Horizon Wavenumber (k_H)         : {K_H_H_MPC:.6e} h/Mpc")
    print(f"  * Action Cutoff Scale (k_trans)    : {K_TRANS:.6f} h/Mpc")

    mass_test_list = [1e15, 1e14, 1e13, 1e12, 1e10]
    redshifts = [0.0, 0.5, 1.0, 2.0]
    
    print("\n[2] NUMERICAL EVALUATION OF COLLAPSE THRESHOLD MATRIX delta_c(z, M):")
    print("-" * 84)
    print(f"{'Mass [h^-1 M_sun]':^18} | {'k [h/Mpc]':^12} | {'z=0.0':^12} | {'z=0.5':^12} | {'z=1.0':^12} | {'z=2.0':^12}")
    print("-" * 84)

    results_table = []
    for m in mass_test_list:
        k_val, _ = mass_to_wavenumber(m)
        d_z0 = spherical_collapse_threshold(m, 0.0)
        d_z05 = spherical_collapse_threshold(m, 0.5)
        d_z1 = spherical_collapse_threshold(m, 1.0)
        d_z2 = spherical_collapse_threshold(m, 2.0)
        
        results_table.append({
            'mass': m,
            'k': k_val,
            'delta_c_z0.0': d_z0,
            'delta_c_z0.5': d_z05,
            'delta_c_z1.0': d_z1,
            'delta_c_z2.0': d_z2
        })
        
        print(f"{m:^18.1e} | {k_val:^12.4f} | {d_z0:^12.5f} | {d_z05:^12.5f} | {d_z1:^12.5f} | {d_z2:^12.5f}")

    print("-" * 84)

    # Generate figure in current execution folder
    mass_array = np.logspace(10, 15, 300)
    fig_filename = "figure_19_1_spherical_collapse.png"
    fig_path = generate_visuals(mass_array, redshifts, output_filename=fig_filename)
    
    print("\n[3] VISUAL GRAPHIC ASSET GENERATED:")
    print(f"  * Rendered Figure Asset -> {os.path.abspath(fig_path)}")

    sec19_data_payload = {
        'section_id': 19,
        'title': 'Spherical & Ellipsoidal Halo Collapse Engine delta_c(z, M)',
        'a_crit': A_CRIT,
        'delta_c_0': DELTA_C_0,
        'k_trans': K_TRANS,
        'table': results_table,
        'figure_path': os.path.abspath(fig_path)
    }

    print("\n[Section 19 Execution Complete]\n")
    return sec19_data_payload


if __name__ == "__main__":
    run_section_19()