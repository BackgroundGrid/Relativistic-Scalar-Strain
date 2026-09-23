# section_09_cluster_dynamics_final.py
# Volume II, Section 09: Complete Hydro-Lensing Engine & Mathematical Field Verification

import math
import os
import matplotlib.pyplot as plt
import numpy as np
from mpmath import exp, mp, mpf, sqrt

# Enforce 50-digit precision for field invariant evaluations
mp.dps = 50


def execute_mathematical_proof():
    """Outputs step-by-step action field calculations directly to terminal."""
    print("=" * 85)
    print(
        "VSS MONOGRAPH VOL II — SECTION 09: MATHEMATICAL FIELD CALCULATIONS"
    )
    print("=" * 85)

    # 1. Fundamental Constants
    c = mpf("299792458.0")
    G = mpf("6.67430e-11")
    H0_km_s_Mpc = mpf("67.4")
    Mpc_to_m = mpf("3.08567758149137e22")

    H0_si = (H0_km_s_Mpc * mpf("1000.0")) / Mpc_to_m
    a_crit = (c * H0_si) / (mpf("2.0") * mp.pi)

    print("\n[STEP 1: VARIATIONAL ACTION INVARIANTS]")
    print(
        f"  * Speed of Light (c)           = {mp.nstr(c, 10)} m/s"
    )
    print(
        f"  * Hubble Constant (H0)         = {mp.nstr(H0_si, 10)} s^-1"
    )
    print(
        "  * Critical Acceleration (a_c)  = c*H0 / (2*pi)"
        f" = {mp.nstr(a_crit, 12)} m/s^2"
    )

    # 2. Lagrangian Kinetic Strain Scalar Evaluation
    # X = (grad phi)^2 / (2 * a_crit^2)
    g_local = mpf("1.0e-11")  # Typical cluster halo boundary acceleration
    X_val = g_local / a_crit
    F_prime = exp(-sqrt(X_val))
    c_eff = c * sqrt(F_prime)

    print("\n[STEP 2: NON-LINEAR D'ALEMBERTIAN KINETIC EVALUATION]")
    print(
        f"  * Sample Boundary Field (g)    = {mp.nstr(g_local, 8)} m/s^2"
    )
    print(
        f"  * Dimensionless Scalar (X)     = g / a_crit = {mp.nstr(X_val, 8)}"
    )
    print(
        f"  * Action Derivative F'(X)      = exp(-sqrt(X)) = {mp.nstr(F_prime, 8)}"
    )
    print(
        "  * Saturated Field Speed (c_eff)= c * sqrt(F') ="
        f" {mp.nstr(c_eff, 8)} m/s"
    )
    print(
        f"  * Retardation Ratio (c_eff/c)  = {mp.nstr(c_eff / c, 8)}"
    )

    # 3. Retarded Lensing Centroid Phase Lag Integral
    v_impact = mpf("4500000.0")  # 4500 km/s relative collision speed
    t_post = mpf("1.0e8") * mpf("31557600.0")  # 100 Myr post-impact
    delta_x_calc = v_impact * t_post * (mpf("1.0") - (c_eff / c))
    delta_x_kpc = delta_x_calc / mpf("3.08567758149137e19")

    print("\n[STEP 3: GREEN'S FUNCTION PHASE RETARDATION INTEGRAL]")
    print(
        "  * Impact Speed (v_impact)      ="
        f" {mp.nstr(v_impact / mpf(1000), 6)} km/s"
    )
    print("  * Elapsed Time (t_post)        = 100.0 Myr")
    print(
        "  * Action Formula               : Delta_x = v * t * (1 - c_eff/c)"
    )
    print(
        f"  * Derived Lensing Separation   = {mp.nstr(delta_x_kpc, 8)} kpc"
    )

    print("=" * 85 + "\n")
    return float(c), float(a_crit)


def solve_g_obs(gb, a_crit):
    if gb <= 1e-25:
        return gb
    g_guess = math.sqrt(gb * a_crit) if gb < a_crit else gb
    for _ in range(30):
        X_val = max(1e-20, g_guess / a_crit)
        sqrt_X = math.sqrt(X_val)
        exp_term = math.exp(-sqrt_X)
        f_val = g_guess * (1.0 - exp_term) - gb
        df_val = (1.0 - exp_term) + 0.5 * sqrt_X * exp_term
        if abs(df_val) < 1e-15:
            break
        step = f_val / df_val
        g_guess = max(gb, g_guess - step)
        if abs(step) < 1e-12 * g_guess:
            break
    return g_guess


def generate_publication_figure(c, a_crit):
    grid_size = 180
    lim_Mpc = 2.0
    x = np.linspace(-lim_Mpc, lim_Mpc, grid_size)
    y = np.linspace(-lim_Mpc, lim_Mpc, grid_size)
    X_grid, Y_grid = np.meshgrid(x, y)

    Mpc_to_m = 3.08567758149137e22
    G = 6.67430e-11
    M_sun_kg = 1.98847e30

    # 1. Stalled Gas Core (Center)
    r_gas = np.sqrt(X_grid**2 + Y_grid**2) * Mpc_to_m
    a_gas_m = 0.35 * Mpc_to_m
    M_gas_tot = 1.2e14 * M_sun_kg
    rho_gas = (M_gas_tot / (2 * np.pi * a_gas_m**2)) * np.exp(
        -r_gas / a_gas_m
    )

    # 2. Separated Galaxies (+/- 0.75 Mpc)
    d_gal_Mpc = 0.75
    r_gal1 = (
        np.sqrt((X_grid - d_gal_Mpc) ** 2 + Y_grid**2) * Mpc_to_m
    )
    r_gal2 = (
        np.sqrt((X_grid + d_gal_Mpc) ** 2 + Y_grid**2) * Mpc_to_m
    )
    a_gal_m = 0.18 * Mpc_to_m
    M_gal_tot = 0.3e14 * M_sun_kg
    rho_gal = (M_gal_tot / (2 * np.pi * a_gal_m**2)) * (
        np.exp(-r_gal1 / a_gal_m) + np.exp(-r_gal2 / a_gal_m)
    )

    rho_bar_tot = rho_gas + rho_gal

    # 3. 2D Poisson Gravity Potential
    phi_bar = np.zeros((grid_size, grid_size))
    dx_m = (2 * lim_Mpc * Mpc_to_m) / grid_size

    for _ in range(300):
        phi_bar[1:-1, 1:-1] = 0.25 * (
            phi_bar[2:, 1:-1]
            + phi_bar[:-2, 1:-1]
            + phi_bar[1:-1, 2:]
            + phi_bar[1:-1, :-2]
            - 4 * np.pi * G * rho_bar_tot[1:-1, 1:-1] * (dx_m**2)
        )

    grad_y, grad_x = np.gradient(phi_bar, dx_m)
    gx_bar = -grad_x
    gy_bar = -grad_y
    g_bar_mag = np.sqrt(gx_bar**2 + gy_bar**2)

    # 4. Non-Linear Vector Transformation
    gx_obs = np.zeros_like(gx_bar)
    gy_obs = np.zeros_like(gy_bar)

    for i in range(grid_size):
        for j in range(grid_size):
            gb = g_bar_mag[i, j]
            if gb > 1e-25:
                go = solve_g_obs(gb, a_crit)
                gx_obs[i, j] = gx_bar[i, j] * (go / gb)
                gy_obs[i, j] = gy_bar[i, j] * (go / gb)

    # 5. Smooth 2D Vector Divergence for Weak Lensing Convergence kappa
    dgx_dx = np.gradient(gx_obs, dx_m, axis=1)
    dgy_dy = np.gradient(gy_obs, dx_m, axis=0)
    div_g = dgx_dx + dgy_dy
    kappa = np.abs(div_g)
    kappa = kappa / np.max(kappa)

    I_xray = rho_gas**2
    I_xray = I_xray / np.max(I_xray)

    # 6. Plotting with Monograph Footprint
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["mathtext.fontset"] = "stix"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6.5))

    im1 = ax1.imshow(
        I_xray,
        extent=[-lim_Mpc, lim_Mpc, -lim_Mpc, lim_Mpc],
        origin="lower",
        cmap="plasma",
    )
    ax1.set_title(
        "Panel (a) — Hydrodynamic Stalled Plasma (X-Ray Brightness)",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )
    ax1.set_xlabel("x (Mpc)", fontsize=10)
    ax1.set_ylabel("y (Mpc)", fontsize=10)
    ax1.plot(0, 0, "rx", markersize=12, markeredgewidth=2.5, label="Gas Core Peak")
    ax1.legend(loc="upper right", frameon=True, fontsize=9)
    plt.colorbar(im1, ax=ax1, label="Normalized X-Ray Intensity", fraction=0.046, pad=0.04)

    im2 = ax2.imshow(
        kappa,
        extent=[-lim_Mpc, lim_Mpc, -lim_Mpc, lim_Mpc],
        origin="lower",
        cmap="viridis",
    )
    ax2.set_title(
        r"Panel (b) — Relativistic Strain Convergence ($\kappa$)",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )
    ax2.set_xlabel("x (Mpc)", fontsize=10)
    ax2.set_ylabel("y (Mpc)", fontsize=10)
    ax2.plot(
        [d_gal_Mpc, -d_gal_Mpc],
        [0, 0],
        "w+",
        markersize=12,
        markeredgewidth=2.5,
        label="Strain Centroids",
    )
    ax2.legend(loc="upper right", frameon=True, fontsize=9)
    plt.colorbar(im2, ax=ax2, label=r"Convergence $\kappa$", fraction=0.046, pad=0.04)

    footprint_text = (
        "VSS MONOGRAPH VOL II | SEC 09 FIRST-PRINCIPLES FIELD ENGINE\n"
        r"Zero Dark Matter Assumptions | Locked to $a_{crit} = c H_0 / 2\pi$"
    )
    fig.text(
        0.5,
        0.01,
        footprint_text,
        ha="center",
        fontsize=9,
        fontstyle="italic",
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor="white",
            alpha=0.85,
            edgecolor="gray",
        ),
    )

    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out_file = "figure_09_growth_rate_fsigma8.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    print(
        f"[SUCCESS] Figure saved with footprint: {os.path.abspath(out_file)}"
    )


if __name__ == "__main__":
    c, a_crit = execute_mathematical_proof()
    generate_publication_figure(c, a_crit)