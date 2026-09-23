# section_08_variational_action.py
# Volume II, Section 08: 100% First-Principles Pure Closed-Form Audit

import math
import os
import matplotlib.pyplot as plt
import numpy as np
from mpmath import exp, mp, mpf, sqrt

# Set arbitrary precision to 50 decimal digits (256-bit mantissa)
mp.dps = 50


def F_exact_closed_form(X_val, a_crit_val):
    """100% Pure Analytical Closed-Form Strain Lagrangian (Zero Taylor Series)."""
    X_mp = mpf(X_val)
    a_mp = mpf(a_crit_val)
    g_mp = sqrt(mpf(2.0) * X_mp)
    y_mp = g_mp / a_mp

    return X_mp + a_mp * g_mp * exp(-y_mp) + (a_mp**2) * (exp(-y_mp) - mpf(1.0))


def run_first_principles_audit():
    c = mpf("299792458.0")
    H0_km_s_Mpc = mpf("67.4")
    Mpc_to_m = mpf("3.08567758149137e22")

    H0_si = (H0_km_s_Mpc * mpf("1000.0")) / Mpc_to_m
    a_crit = (c * H0_si) / (mpf("2.0") * mp.pi)
    Omega_vac = mpf("1.0") - (mpf("1.0") / mp.pi)

    print("=" * 100)
    print(
        "   SECTION 08: 100% FIRST-PRINCIPLES EXACT CLOSED-FORM AUDIT (50-DIGIT"
        " PRECISION)"
    )
    print("=" * 100)
    print(f"Speed of Light (c)             : {mp.nstr(c, 15)} m/s")
    print(
        "Hubble Constant (H0)           :"
        f" {mp.nstr(H0_km_s_Mpc, 8)} km/s/Mpc"
    )
    print(f"Hubble Frequency (H0_si)       : {mp.nstr(H0_si, 12)} s^-1")
    print(f"Derived Critical Acceleration  : {mp.nstr(a_crit, 12)} m/s^2")
    print(f"Derived Vacuum Energy Ratio    : {mp.nstr(Omega_vac, 8)}")
    print("-" * 100)

    header = (
        f"{'g_obs (m/s^2)':<15} | "
        f"{'Hardware Float64 (Broken)':<26} | "
        f"{'mpmath Exact (50-Digit Valid)':<32} | "
        f"{'Diagnostic Benchmark':<20}"
    )
    print(header)
    print("-" * 100)

    test_g = [1e-2, 1e-8, float(a_crit), 1e-12, 1e-14, 1e-16]
    for g_val in test_g:
        X_val = 0.5 * (g_val**2)

        # Standard float64 evaluation
        try:
            g_f64 = math.sqrt(2.0 * X_val)
            y_f64 = g_f64 / float(a_crit)
            f_f64 = (
                X_val
                + float(a_crit) * g_f64 * math.exp(-y_f64)
                + (float(a_crit) ** 2) * (math.exp(-y_f64) - 1.0)
            )
        except Exception:
            f_f64 = 0.0

        # Exact mpmath 50-digit evaluation
        f_exact = F_exact_closed_form(X_val, a_crit)

        status = (
            "Float64 Hardware Loss"
            if (f_f64 <= 0 or abs(f_f64 - float(f_exact)) / float(f_exact) > 0.1)
            else "Exact Agreement"
        )
        print(
            f"{g_val:<15.4e} | {f_f64:<26.10e} | {mp.nstr(f_exact, 15):<32} |"
            f" {status:<20}"
        )

    print("=" * 100 + "\n")
    return float(c), float(H0_km_s_Mpc), float(Mpc_to_m), float(a_crit)


def generate_clean_figure(c, H0_km_s_Mpc, Mpc_to_m, a_crit):
    g_vals = np.logspace(-16, -2, 400)
    X_vals = 0.5 * (g_vals**2)

    a_crit_mp = mpf(a_crit)
    F_exact_vals = [
        float(F_exact_closed_form(x, a_crit_mp)) for x in X_vals
    ]

    # Matplotlib font rendering configurations
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["mathtext.fontset"] = "stix"
    # Prevents clipping/dropping minus signs on logarithmic tick labels
    plt.rcParams["axes.unicode_minus"] = False

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Panel (a): Pure Exact Field Action
    ax1.loglog(
        g_vals,
        F_exact_vals,
        label=r"Exact Closed-Form $\mathcal{F}(X)$ (50-Digit Precision)",
        color="#2980b9",
        linewidth=2.5,
    )
    ax1.axvspan(
        1e-16,
        1e-13,
        color="#c0392b",
        alpha=0.12,
        label="Float64 Hardware Cancellation Zone",
    )
    ax1.set_ylim(1e-40, 1e-4)
    ax1.set_title(
        "Panel (a) — Pure First-Principles Strain Action",
        fontsize=11,
        fontweight="bold",
    )
    ax1.set_xlabel(
        r"Observed Acceleration $g_{\text{obs}}$ (m/s$^2$)", fontsize=10
    )
    ax1.set_ylabel(
        r"Strain Lagrangian $\mathcal{F}(X)$ (m$^2$/s$^4$)", fontsize=10
    )
    ax1.grid(True, which="both", linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left", frameon=True, fontsize=9)

    # Panel (b): Universal Boundary Derivation
    H0_range = np.linspace(65, 70, 300)
    a_crit_range = (c * ((H0_range * 1000.0) / Mpc_to_m)) / (2.0 * math.pi)

    ax2.plot(
        H0_range,
        a_crit_range,
        color="#e67e22",
        linewidth=2.5,
        label=r"$a_{\text{crit}} \equiv \frac{c H_0}{2\pi}$",
    )
    ax2.axvline(H0_km_s_Mpc, color="#7f8c8d", linestyle="--", linewidth=1)
    ax2.axhline(a_crit, color="#7f8c8d", linestyle="--", linewidth=1)
    ax2.plot(H0_km_s_Mpc, a_crit, "ro", markersize=7, label="Planck 2018 Point")

    callout_text = (
        "Derived Invariant:\n"
        f"$a_c = 1.0422 \\times 10^{{-10}}$ m/s$^2$\n"
        f"$H_0 = 67.4$ km/s/Mpc\n"
        "Free Parameters: NONE"
    )
    ax2.text(
        65.3,
        1.07e-10,
        callout_text,
        fontsize=9,
        bbox=dict(
            boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#bdc3c7"
        ),
    )
    ax2.set_title(
        "Panel (b) — Axiomatic Boundary Mapping",
        fontsize=11,
        fontweight="bold",
    )
    ax2.set_xlabel(r"Hubble Constant $H_0$ (km/s/Mpc)", fontsize=10)
    ax2.set_ylabel(r"Critical Acceleration $a_{\text{crit}}$ (m/s$^2$)", fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="lower right", frameon=True, fontsize=9)

    plt.tight_layout()

    out_file = "figure_08_gauge_invariant_perturbations.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    print(f"Saved figure file to disk: {os.path.abspath(out_file)}")

    plt.show()


if __name__ == "__main__":
    c, H0_km_s_Mpc, Mpc_to_m, a_crit = run_first_principles_audit()
    generate_clean_figure(c, H0_km_s_Mpc, Mpc_to_m, a_crit)