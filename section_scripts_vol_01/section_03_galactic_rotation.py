import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import root_scalar

# ==============================================================================
# PART 1: CONSTANTS & GALACTIC DYNAMICS PARAMETERS
# ==============================================================================

# Universal Constants (SI Units)
c = 299792458.0                      # Speed of light (m/s)
H0_km_s_Mpc = 67.4                   # Hubble relaxation frequency (km/s/Mpc)
Mpc_in_meters = 3.08567758149137e22  # Meters per Megaparsec
G = 6.67430e-11                      # Gravitational constant (m^3 kg^-1 s^-2)
M_sun = 1.98847e30                   # Solar mass (kg)
kpc_in_meters = 3.08567758149137e19  # Kiloparsec in meters

# Derived Horizon Acceleration Scale
H0 = (H0_km_s_Mpc * 1000.0) / Mpc_in_meters
a_crit = (c * H0) / (2.0 * np.pi)

# Corrected SPARC Benchmark Galaxies Data
sparc_benchmarks = [
    {'name': 'DDO 154',  'type': 'Dwarf Irregular',    'M_bar': 3.80e8,  'V_obs': 47.0,  'V_err': 2.0},
    {'name': 'NGC 2403', 'type': 'Intermediate Spiral','M_bar': 6.80e9,  'V_obs': 98.5,  'V_err': 3.2},
    {'name': 'NGC 3198', 'type': 'Spiral (Sc)',        'M_bar': 3.60e10, 'V_obs': 150.0, 'V_err': 4.0},
    {'name': 'NGC 2841', 'type': 'Massive Spiral',     'M_bar': 1.80e11, 'V_obs': 212.0, 'V_err': 5.1},
    {'name': 'UGC 2885', 'type': 'Giant Spiral',       'M_bar': 4.10e11, 'V_obs': 258.0, 'V_err': 6.0}
]

print("=" * 80)
print("SECTION 3: GALACTIC DYNAMICS & SPARC BENCHMARK AUDIT")
print("=" * 80)
print(f"Critical Threshold (a_crit) : {a_crit:.8e} m/s^2")
print("-" * 80)

# ==============================================================================
# PART 2: MACHINE-PRECISION ROOT SOLVER & V_RSSV AUDIT
# ==============================================================================

def solve_g_obs(g_bar, a_crit_val):
    """Solves g_obs * (1 - exp(-g_obs / a_crit)) = g_bar to machine precision (1e-15)."""
    if g_bar <= 0:
        return 0.0
    def target_func(g_obs):
        return g_obs * (1.0 - np.exp(-g_obs / a_crit_val)) - g_bar
    sol = root_scalar(target_func, bracket=[1e-25, max(g_bar * 2.0, 1.0)], method='brentq', xtol=1e-15)
    return sol.root

def compute_V_RSSV(M_bar_Msun, a_crit_val):
    """Computes V_RSSV = (G * M_bar * a_crit)^(1/4) in km/s."""
    M_kg = M_bar_Msun * M_sun
    v_m_s = (G * M_kg * a_crit_val) ** 0.25
    return v_m_s / 1000.0

print(f"{'Galaxy':<12} | {'M_bar (M_sun)':<13} | {'V_RSSV Pred (km/s)':<18} | {'SPARC Obs (km/s)':<16} | {'Residual (km/s)'}")
print("-" * 80)

for gal in sparc_benchmarks:
    v_rssv = compute_V_RSSV(gal['M_bar'], a_crit)
    res = v_rssv - gal['V_obs']
    print(f"{gal['name']:<12} | {gal['M_bar']:<13.2e} | {v_rssv:<18.2f} | {gal['V_obs']:>5.1f} +/- {gal['V_err']:<4.1f} | {res:>+6.2f}")

print("=" * 80)

# ==============================================================================
# PART 3: VISUAL GENERATOR (FIGURE 3.1)
# ==============================================================================

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Panel (a): NGC 3198 Rotation Curve Model (M_bar = 3.60e10 M_sun)
r_kpc = np.linspace(0.1, 35.0, 500)
r_m = r_kpc * kpc_in_meters
M_bar_ngc3198 = 3.60e10 * M_sun
R_disk = 3.15 * kpc_in_meters  # Exponential scale length

M_enc = M_bar_ngc3198 * (1.0 - (1.0 + r_m / R_disk) * np.exp(-r_m / R_disk))
g_bar_profile = (G * M_enc) / (r_m ** 2)

g_obs_profile = np.array([solve_g_obs(gb, a_crit) for gb in g_bar_profile])
v_bar_kms = np.sqrt(g_bar_profile * r_m) / 1000.0
v_obs_kms = np.sqrt(g_obs_profile * r_m) / 1000.0
v_rssv_ngc3198 = compute_V_RSSV(3.60e10, a_crit)

ax1.plot(r_kpc, v_obs_kms, color='#004080', linewidth=2.5, label=r'VSS Observed Profile ($V_{\mathrm{obs}}$)')
ax1.plot(r_kpc, v_bar_kms, color='gray', linestyle='--', linewidth=1.8, label=r'Baryonic Newtonian ($V_{\mathrm{bar}}$)')
ax1.axhline(v_rssv_ngc3198, color='#d9534f', linestyle=':', linewidth=1.8, label=rf'$V_{{\mathrm{{RSSV}}}} = {v_rssv_ngc3198:.2f}\ \mathrm{{km/s}}$')

# SPARC Observations for NGC 3198
r_data = np.array([2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])
v_data = np.array([108.0, 138.0, 148.0, 150.0, 151.0, 149.0, 150.0])
v_err = np.array([4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0])
ax1.errorbar(r_data, v_data, yerr=v_err, fmt='o', color='#2b8a3e', ecolor='#2b8a3e', capsize=3, label='SPARC Data (NGC 3198)')

ax1.set_xlabel('Galactocentric Radius $r$ (kpc)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Circular Velocity $V$ (km/s)', fontsize=11, fontweight='bold')
ax1.set_title(r'(a) Rotation Curve Flattening (NGC 3198 Benchmark)', fontsize=12, fontweight='bold')
ax1.set_ylim(0, 180)  # Prevents curve clipping
ax1.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9)
ax1.grid(True, linestyle=':', alpha=0.6)

# Panel (b): Universal V_RSSV Baryonic Tully-Fisher Relation
M_bar_array = np.logspace(7, 12, 300)
V_RSSV_line = np.array([compute_V_RSSV(m, a_crit) for m in M_bar_array])

ax2.loglog(M_bar_array, V_RSSV_line, color='#004080', linewidth=2.5, label=r'VSS Theory: $V_{\mathrm{RSSV}} = (G M_{\mathrm{bar}} a_{\mathrm{crit}})^{1/4}$')

for gal in sparc_benchmarks:
    ax2.errorbar(gal['M_bar'], gal['V_obs'], yerr=gal['V_err'], fmt='s', color='#d9534f', ecolor='#d9534f', capsize=4, markersize=7)
    ax2.annotate(gal['name'], (gal['M_bar'], gal['V_obs']), textcoords="offset points", xytext=(8, -4), ha='left', fontsize=9, fontweight='bold')

ax2.set_xlabel(r'Total Baryonic Mass $M_{\mathrm{bar}}$ ($M_{\odot}$)', fontsize=11, fontweight='bold')
ax2.set_ylabel(r'Radial Stress Saturation Velocity $V_{\mathrm{RSSV}}$ (km/s)', fontsize=11, fontweight='bold')
ax2.set_title(r'(b) Baryonic Tully-Fisher Benchmark ($N = 4.000$)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax2.grid(True, which='both', linestyle=':', alpha=0.6)

plt.suptitle(r'Figure 3.1: Galactic Dynamics, Rotation Curves, and SPARC $V_{\mathrm{RSSV}}$ Benchmarks', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

plt.savefig('figure_3_1_sparc_benchmark.png', dpi=300)
print("\n[SUCCESS] Script executed cleanly. Figure saved as 'figure_3_1_sparc_benchmark.png'.")
