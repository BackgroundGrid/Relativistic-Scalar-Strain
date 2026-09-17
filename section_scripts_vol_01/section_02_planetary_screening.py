import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# PART 1: CONSTANTS & SOLAR SYSTEM PHYSICAL PARAMETERS
# ==============================================================================

# Universal Constants (SI Units)
c = 299792458.0                      # Speed of light (m/s)
H0_km_s_Mpc = 67.4                   # Hubble relaxation frequency (km/s/Mpc)
Mpc_in_meters = 3.08567758149137e22  # Meters per Megaparsec
G = 6.67430e-11                      # Gravitational constant (m^3 kg^-1 s^-2)
M_sun = 1.98847e30                   # Solar mass (kg)
AU_in_meters = 1.495978707e11        # Astronomical Unit (m)

# Derived Threshold
H0 = (H0_km_s_Mpc * 1000.0) / Mpc_in_meters
a_crit = (c * H0) / (2.0 * np.pi)

# Solar System Benchmark Objects (Distance in AU)
solar_system_targets = {
    'Mercury': 0.387,
    'Earth': 1.000,
    'Saturn': 9.580,
    'Kuiper Belt': 40.0,
    'Oort Cloud': 10000.0
}

# Empirical Constraints (m/s^2)
cassini_bound = 1e-14

print("=" * 75)
print("SECTION 2: SOLAR SYSTEM SCREENING & CASSINI AUDIT")
print("=" * 75)
print(f"Critical Threshold (a_crit) : {a_crit:.8e} m/s^2")
print(f"Cassini Precision Bound     : {cassini_bound:.1e} m/s^2")
print("-" * 75)

# ==============================================================================
# PART 2: EXPONENTIAL SCREENING NUMERICAL AUDIT
# ==============================================================================

print(f"{'Target':<15} | {'Radius (AU)':<11} | {'g_bar (m/s^2)':<13} | {'Ratio (x)':<12} | {'Residual dg (m/s^2)'}")
print("-" * 75)

for name, r_au in solar_system_targets.items():
    r_m = r_au * AU_in_meters
    g_bar = (G * M_sun) / (r_m ** 2)
    x = g_bar / a_crit
    
    if x > 700:  # Exceeds double float range e^-700 ~ 1e-304
        dg_str = "< 1e-300 (Fully Screened)"
    else:
        dg = g_bar * np.exp(-x)
        dg_str = f"{dg:.4e}"
        
    print(f"{name:<15} | {r_au:<11.3f} | {g_bar:<13.4e} | {x:<12.3e} | {dg_str}")

print("=" * 75)

# ==============================================================================
# PART 3: VISUAL GENERATOR (FIGURE 2.1)
# ==============================================================================

# Radial Array from 0.1 AU to 100,000 AU (Log Scale)
r_au_array = np.logspace(-1, 5, 1000)
r_m_array = r_au_array * AU_in_meters
g_bar_array = (G * M_sun) / (r_m_array ** 2)
x_array = g_bar_array / a_crit

# Calculate residual perturbational acceleration
exp_arg = np.clip(-x_array, -700, 700)
dg_array = g_bar_array * np.exp(exp_arg)
saturation_factor = 1.0 - np.exp(exp_arg)

r_saturn = solar_system_targets['Saturn']

# Initialize figure and axes
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# Panel (a): Residual Acceleration vs Cassini Limit
ax1.loglog(r_au_array, dg_array, color='#004080', linewidth=2.5, label=r'VSS Residual: $\delta g = g_{\mathrm{bar}} e^{-g_{\mathrm{bar}}/a_{\mathrm{crit}}}$')
ax1.axhline(cassini_bound, color='#d9534f', linestyle='--', linewidth=1.8, label=r'Cassini Precision Limit ($10^{-14}\ \mathrm{m/s}^2$)')
ax1.axvline(r_saturn, color='#5bc0de', linestyle='-.', alpha=0.8, label=rf'Saturn (9.58 AU): $\delta g \ll 10^{{-100}}$')

ax1.set_xlabel('Heliospheric Distance $r$ (AU)', fontsize=11, fontweight='bold')
ax1.set_ylabel(r'Anomalous Acceleration Residual $\delta g$ (m/s$^2$)', fontsize=11, fontweight='bold')
ax1.set_title(r'(a) VSS Exponential Screening Suppression', fontsize=12, fontweight='bold')
ax1.set_ylim(1e-20, 1e-8)
ax1.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
ax1.grid(True, which='both', linestyle=':', alpha=0.6)

# Panel (b): Continuum Strain Saturation Factor S(x)
ax2.semilogx(r_au_array, saturation_factor * 100.0, color='#2b8a3e', linewidth=2.5, label=r'Strain Saturation: $S(x) = 1 - e^{-x}$')
ax2.axvline(r_saturn, color='#5bc0de', linestyle='-.', alpha=0.8, label=r'Saturn (9.58 AU)')
ax2.axhline(100.0, color='gray', linestyle=':', alpha=0.7)

ax2.set_xlabel('Heliospheric Distance $r$ (AU)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Spatial Continuum Saturation Level (%)', fontsize=11, fontweight='bold')
ax2.set_title(r'(b) Solar System Vacuum Elastic Saturation Profile', fontsize=12, fontweight='bold')
ax2.set_ylim(-5, 105)
ax2.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9)
ax2.grid(True, which='both', linestyle=':', alpha=0.6)

plt.suptitle(r'Figure 2.1: Solar System Exponential Screening & Cassini Validation', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

# Save image
plt.savefig('figure_2_1_solar_screening.png', dpi=300)
print("\n[SUCCESS] Script executed cleanly. Figure saved as 'figure_2_1_solar_screening.png'.")
