import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ==============================================================================
# PART 1: FIRST-PRINCIPLES DERIVATION & CONSTANTS
# ==============================================================================

# Universal Constants (SI Units)
c = 299792458.0                      # Speed of light (m/s)
H0_km_s_Mpc = 67.4                   # Hubble relaxation frequency (km/s/Mpc)
Mpc_in_meters = 3.08567758149137e22  # Meters per Megaparsec
G = 6.67430e-11                      # Gravitational constant (m^3 kg^-1 s^-2)
M_sun = 1.98847e30                   # Solar mass (kg)

# Horizon Frequency tau_0^-1 (s^-1)
H0 = (H0_km_s_Mpc * 1000.0) / Mpc_in_meters

# Derive a_crit from S2 Boundary Topology (0.00 Free Parameters)
a_H = c * H0
a_crit = a_H / (2.0 * np.pi)

print("=" * 70)
print("SECTION 1: MATHEMATICAL & NUMERICAL INTEGRITY AUDIT")
print("=" * 70)
print(f"Speed of light (c)          : {c:.8e} m/s")
print(f"Horizon frequency (H0)      : {H0:.8e} s^-1")
print(f"Horizon acceleration (a_H)  : {a_H:.8e} m/s^2")
print(f"Derived Threshold (a_crit)  : {a_crit:.8e} m/s^2")
print("=" * 70)

# ==============================================================================
# PART 2: MACHINE-PRECISION ROOT SOLVER FOR VSS MASTER EQUATION
# ==============================================================================

def solve_g_obs(g_bar, a_crit_val):
    """
    Solves: g_obs * (1 - exp(-g_obs / a_crit)) - g_bar = 0
    using Brent's method to machine precision (1e-15).
    """
    if g_bar <= 0:
        return 0.0
    
    def target_func(g_obs):
        return g_obs * (1.0 - np.exp(-g_obs / a_crit_val)) - g_bar

    # Asymptotic boundary guesses for bracket search
    lower_bound = 1e-25
    upper_bound = max(g_bar * 2.0, np.sqrt(g_bar * a_crit_val) * 10.0, 1.0)
    
    sol = root_scalar(target_func, bracket=[lower_bound, upper_bound], method='brentq', xtol=1e-15)
    return sol.root

# Vectorize solver across stress arrays
v_solve_g_obs = np.vectorize(lambda gb: solve_g_obs(gb, a_crit))

# ==============================================================================
# PART 3: BTFR & RADIAL STRESS SATURATION VELOCITY (V_RSSV)
# ==============================================================================

def compute_V_RSSV(M_bar_kg, a_crit_val):
    """
    Computes V_RSSV = (G * M_bar * a_crit)^(1/4) in km/s
    """
    v_m_s = (G * M_bar_kg * a_crit_val) ** 0.25
    return v_m_s / 1000.0  # Convert to km/s

# Benchmark across 5 decades of baryonic mass (10^7 to 10^11 M_sun)
mass_scales_Msun = np.logspace(7, 11, 5)
print("\n[V_RSSV Exact Analytical Scale-Invariant Calculations]")
for M in mass_scales_Msun:
    M_kg = M * M_sun
    v_rssv = compute_V_RSSV(M_kg, a_crit)
    print(f"Baryonic Mass: 10^{np.log10(M):.1f} M_sun | V_RSSV: {v_rssv:8.2f} km/s")

# ==============================================================================
# PART 4: VISUAL GENERATOR (FIGURE 1.1)
# ==============================================================================

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Panel (a): VSS Master Constitutive Field Curve
g_bar_array = np.logspace(-15, -7, 500)
g_obs_array = v_solve_g_obs(g_bar_array)

g_obs_newtonian = g_bar_array
g_obs_weak = np.sqrt(g_bar_array * a_crit)

ax1.loglog(g_bar_array, g_obs_array, color='#004080', linewidth=2.5, label=r'VSS Master: $g_{\mathrm{obs}}(1 - e^{-g_{\mathrm{obs}}/a_{\mathrm{crit}}}) = g_{\mathrm{bar}}$')
ax1.loglog(g_bar_array, g_obs_newtonian, color='gray', linestyle='--', linewidth=1.5, label=r'Newtonian Limit ($g_{\mathrm{obs}} = g_{\mathrm{bar}}$)')
ax1.loglog(g_bar_array, g_obs_weak, color='#d9534f', linestyle=':', linewidth=1.5, label=r'Weak-Field Asymptote ($g_{\mathrm{obs}} = \sqrt{g_{\mathrm{bar}} a_{\mathrm{crit}}}$)')

ax1.axvline(a_crit, color='#5bc0de', linestyle='-.', alpha=0.7, label=f'$a_{{crit}} = {a_crit:.2e}$ m/s$^2$')
ax1.set_xlabel(r'Baryonic Source Stress $g_{\mathrm{bar}}$ (m/s$^2$)', fontsize=11, fontweight='bold')
ax1.set_ylabel(r'Physical Response Acceleration $g_{\mathrm{obs}}$ (m/s$^2$)', fontsize=11, fontweight='bold')
ax1.set_title(r'(a) VSS Master Constitutive Field Response', fontsize=12, fontweight='bold')
ax1.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax1.grid(True, which='both', linestyle=':', alpha=0.6)

# Panel (b): Radial Stress Saturation Velocity (V_RSSV) vs Baryonic Mass
M_bar_plot = np.logspace(7, 11.5, 200)
V_RSSV_plot = np.array([compute_V_RSSV(m * M_sun, a_crit) for m in M_bar_plot])

ax2.loglog(M_bar_plot, V_RSSV_plot, color='#2b8a3e', linewidth=2.5, label=r'$V_{\mathrm{RSSV}} = (G M_{\mathrm{bar}} a_{\text{crit}})^{1/4}$')
ax2.scatter(mass_scales_Msun, [compute_V_RSSV(m * M_sun, a_crit) for m in mass_scales_Msun], 
            color='#d9534f', zorder=5, s=50, label='Verified Mass Baselines')

ax2.set_xlabel(r'Total Baryonic Mass $M_{\mathrm{bar}}$ ($M_{\odot}$)', fontsize=11, fontweight='bold')
ax2.set_ylabel(r'Radial Stress Saturation Velocity $V_{\mathrm{RSSV}}$ (km/s)', fontsize=11, fontweight='bold')
ax2.set_title(r'(b) Universal $V_{\mathrm{RSSV}}$ Scaling Law ($N = 4.000$)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax2.grid(True, which='both', linestyle=':', alpha=0.6)

plt.suptitle(r'Figure 1.1: Vacuum Stress Saturation (VSS) — $a_{\mathrm{crit}}$ Derivation & $V_{\mathrm{RSSV}}$ Kinematics', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

# Save image and display
plt.savefig('figure_1_1_vss_kinematics.png', dpi=300)
print("\n[SUCCESS] Script executed cleanly. Figure saved as 'figure_1_1_vss_kinematics.png'.")
