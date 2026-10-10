"""
Relativistic Scalar Strain (RSS) Architecture - Volume III
Section 18: Non-Local Action Propagator & Metric Slip Engine eta(k, z)
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


# ==============================================================================
# CORE FORMULATIONS & NON-LOCAL PROPAGATOR
# ==============================================================================
def linear_metric_slip(z):
    """Linear cosmological metric slip ratio eta_lin(z) derived in Volume II."""
    return 1.0 - 0.116 * (1.0 + z)**(-0.38)


def scalar_field_propagator(k, k_trans=K_TRANS, gamma=GAMMA_DEFAULT):
    """
    Tree-level Green's function factor S(k) from non-local action S_strain[phi]:
    S(k) = 1 / [1 + (k / k_trans)^gamma]
    """
    k_arr = np.asarray(k, dtype=np.float64)
    return 1.0 / (1.0 + (k_arr / k_trans)**gamma)


def non_linear_metric_slip(k, z, k_trans=K_TRANS, gamma=GAMMA_DEFAULT):
    """
    Scale-dependent metric slip eta(k, z) = 1 + [eta_lin(z) - 1] * S(k)
    - IR Limit (k -> 0)  : eta(k, z) -> eta_lin(z) (Cosmological Slip)
    - UV Limit (k -> inf): eta(k, z) -> 1.000       (Local GR Recovery)
    """
    eta_lin = linear_metric_slip(z)
    s_k = scalar_field_propagator(k, k_trans, gamma)
    return 1.0 + (eta_lin - 1.0) * s_k


def weyl_lensing_ratio(k, z, k_trans=K_TRANS, gamma=GAMMA_DEFAULT):
    """
    Weyl lensing gravitational coupling ratio:
    G_lens / G_matt = (Phi + Psi) / (2 * Psi) = (1 + eta(k, z)) / 2
    """
    eta = non_linear_metric_slip(k, z, k_trans, gamma)
    return 0.5 * (1.0 + eta)


# ==============================================================================
# VISUALIZATION ENGINE (MATCHES VOL 1 & 2 DIRECTORY SAVING CONVENTION)
# ==============================================================================
def generate_visuals(k_array, z_list, output_filename="figure_18_1_nonlinear_metric_slip.png"):
    """
    Generates publication-quality dual-panel graphic.
    Saves image in current working directory / execution folder, matching Vol 1 & 2.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8), dpi=300)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    # OVERALL FIGURE TITLE FOR MONOGRAPH
    fig.suptitle(
        r"Figure 18.1: Scale-Dependent Non-Local Metric Slip $\eta(k, z)$ and Weyl Lensing Coupling",
        fontsize=14,
        fontweight='bold',
        y=0.98
    )

    for z, color in zip(z_list, colors):
        eta_vals = non_linear_metric_slip(k_array, z)
        lens_ratio = weyl_lensing_ratio(k_array, z)

        ax1.semilogx(k_array, eta_vals, label=f'z = {z:.1f}', color=color, lw=2.2)
        ax2.semilogx(k_array, lens_ratio, label=f'z = {z:.1f}', color=color, lw=2.2)

    # Panel 1: Non-Local Metric Slip Propagator
    ax1.axvline(K_TRANS, color='black', linestyle='--', alpha=0.6,
                label=rf'Action Scale $k_{{\mathrm{{trans}}}}={K_TRANS:.3f} \, h/\mathrm{{Mpc}}$')
    ax1.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
    ax1.set_xlabel(r'Wavenumber $k \; [h/\mathrm{Mpc}]$', fontsize=11)
    ax1.set_ylabel(r'Metric Slip Ratio $\eta(k, z) \equiv \Phi / \Psi$', fontsize=11)
    ax1.set_title(r'Non-Local Action Metric Slip Propagator $\eta(k, z)$', fontsize=12, fontweight='bold')
    ax1.grid(True, which="both", ls="--", alpha=0.35)
    ax1.legend(loc='lower right', frameon=True)

    # Panel 2: Weyl Lensing Potential Coupling Ratio
    ax2.axvline(K_TRANS, color='black', linestyle='--', alpha=0.6,
                label=rf'Action Scale $k_{{\mathrm{{trans}}}}={K_TRANS:.3f} \, h/\mathrm{{Mpc}}$')
    ax2.axhline(1.0, color='gray', linestyle=':', alpha=0.5, label='GR Standard Limit (1.0)')
    ax2.set_xlabel(r'Wavenumber $k \; [h/\mathrm{Mpc}]$', fontsize=11)
    ax2.set_ylabel(r'Lensing Gravity Ratio $(1 + \eta)/2$', fontsize=11)
    ax2.set_title(r'Weyl Lensing Potential Coupling Suppression', fontsize=12, fontweight='bold')
    ax2.grid(True, which="both", ls="--", alpha=0.35)
    ax2.legend(loc='lower right', frameon=True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(output_filename, bbox_inches='tight')
    plt.close()
    return output_filename


# ==============================================================================
# MAIN SECTION EXECUTOR (LIVE TERMINAL OUTPUT & STRUCTURED DATA RETURN)
# ==============================================================================
def run_section_18():
    """Executes Section 18 calculations, logs to screen, and outputs figures to execution folder."""
    
    print("=" * 84)
    print(" VSS/RSS MONOGRAPH SERIES - VOLUME III: SECTION 18")
    print(" Non-Local Action Field Propagator & Metric Slip Engine eta(k, z)")
    print("=" * 84)
    
    print("\n[1] ACTION DERIVATION & FIRST-PRINCIPLES CONSTANTS:")
    print(f"  * Speed of Light (c)               : {C_SI:.8e} m/s")
    print(f"  * Hubble Parameter (H0)            : {H0_KM_S_MPC:.2f} km/s/Mpc ({H0_SI:.6e} s^-1)")
    print(f"  * Axiomatic Acceleration (a_crit)  : {A_CRIT:.6e} m/s^2")
    print(f"  * Horizon Wavenumber (k_H)         : {K_H_H_MPC:.6e} h/Mpc")
    print(f"  * Action Cutoff Scale (k_trans)    : {K_TRANS:.6f} h/Mpc")
    print(f"  * Green's Function Exponent (gamma): {GAMMA_DEFAULT:.2f}")

    k_array = np.logspace(-3, 1, 300)
    redshifts = [0.0, 0.5, 1.0, 2.0]
    
    print("\n[2] NUMERICAL EVALUATION OF FIELD PROPAGATOR S(k) & SLIP MATRIX:")
    print("-" * 84)
    print(f"{'Redshift (z)':^12} | {'eta(k->0) [IR Limit]':^20} | {'eta(k=k_trans) [Action]':^22} | {'eta(k->10) [UV GR]':^18}")
    print("-" * 84)

    results_table = []
    for z in redshifts:
        eta_large = non_linear_metric_slip(0.001, z)
        eta_trans = non_linear_metric_slip(K_TRANS, z)
        eta_small = non_linear_metric_slip(10.0, z)
        lens_large = weyl_lensing_ratio(0.001, z)
        
        results_table.append({
            'z': z,
            'eta_large': eta_large,
            'eta_trans': eta_trans,
            'eta_small': eta_small,
            'lens_large': lens_large
        })
        
        print(f"{z:^12.1f} | {eta_large:^20.6f} | {eta_trans:^22.6f} | {eta_small:^18.6f}")

    print("-" * 84)

    # Save directly in current execution path (matches Vol 1 & Vol 2 pathing)
    fig_filename = "figure_18_1_nonlinear_metric_slip.png"
    fig_path = generate_visuals(k_array, redshifts, output_filename=fig_filename)
    
    print("\n[3] VISUAL GRAPHIC ASSET GENERATED:")
    print(f"  * Rendered Figure Asset -> {os.path.abspath(fig_path)}")

    sec18_data_payload = {
        'section_id': 18,
        'title': 'Non-Local Action Field Propagator & Metric Slip Engine eta(k, z)',
        'a_crit': A_CRIT,
        'k_h': K_H_H_MPC,
        'k_trans': K_TRANS,
        'gamma': GAMMA_DEFAULT,
        'table': results_table,
        'figure_path': os.path.abspath(fig_path)
    }

    print("\n[Section 18 Execution Complete]\n")
    return sec18_data_payload


if __name__ == "__main__":
    run_section_18()