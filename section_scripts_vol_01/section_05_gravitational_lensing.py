import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# Universal Constants (SI Units)
c = 299792458.0                      
H0_km_s_Mpc = 67.4                   
Mpc_in_meters = 3.08567758149137e22  
kpc_in_meters = 3.08567758149137e19  
G = 6.67430e-11                      
M_sun = 1.98847e30                   
rad_to_arcsec = (180.0 * 3600.0) / np.pi  

# Derived Horizon Acceleration Scale
H0 = (H0_km_s_Mpc * 1000.0) / Mpc_in_meters
a_crit = (c * H0) / (2.0 * np.pi)

lensing_benchmarks = [
    {'name': 'Q0957+561',     'M_bar': 2.10e11, 'd_geom': 0.655, 'theta_obs': 1.20,  'theta_err': 0.05},
    {'name': 'CASTLES J0158', 'M_bar': 4.80e11, 'd_geom': 0.662, 'theta_obs': 1.80,  'theta_err': 0.08},
    {'name': 'MS 1358+62',    'M_bar': 8.20e13, 'd_geom': 0.430, 'theta_obs': 13.50, 'theta_err': 0.50},
    {'name': 'Abell 1689',    'M_bar': 1.45e14, 'd_geom': 0.431, 'theta_obs': 18.30, 'theta_err': 0.70}
]

def compute_theta_VSS_analytical(M_bar_Msun, a_crit_val):
    M_kg = M_bar_Msun * M_sun
    v_rssv_sq = np.sqrt(G * M_kg * a_crit_val)
    return (2.0 * np.pi * v_rssv_sq) / (c ** 2)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

# --- Panel (a): Corrected Unclipped Deflection Profile ---
b_kpc_array = np.logspace(0, 2.7, 300)
M_galaxy = 2.10e11 * M_sun
M_cluster = 1.45e14 * M_sun

theta_vss_gal = (compute_theta_VSS_analytical(2.10e11, a_crit) * rad_to_arcsec) * np.ones_like(b_kpc_array)
theta_vss_clus = (compute_theta_VSS_analytical(1.45e14, a_crit) * rad_to_arcsec) * np.ones_like(b_kpc_array)

b_m_array = b_kpc_array * kpc_in_meters
theta_newt_gal = ((4.0 * G * M_galaxy) / ((c ** 2) * b_m_array)) * rad_to_arcsec
theta_newt_clus = ((4.0 * G * M_cluster) / ((c ** 2) * b_m_array)) * rad_to_arcsec

ax1.loglog(b_kpc_array, theta_vss_clus, color='#004080', linewidth=2.5, label=r'VSS Cluster Deflection ($\theta_{\mathrm{VSS}} = \mathrm{const}$)')
ax1.loglog(b_kpc_array, theta_newt_clus, color='#004080', linestyle='--', linewidth=1.8, label=r'Newtonian Cluster ($1/b$ decay)')

ax1.loglog(b_kpc_array, theta_vss_gal, color='#2b8a3e', linewidth=2.5, label=r'VSS Galaxy Deflection ($\theta_{\mathrm{VSS}} = \mathrm{const}$)')
ax1.loglog(b_kpc_array, theta_newt_gal, color='#2b8a3e', linestyle='--', linewidth=1.8, label=r'Newtonian Galaxy ($1/b$ decay)')

ax1.set_xlabel('Impact Parameter $b$ (kpc)', fontsize=11, fontweight='bold')
ax1.set_ylabel(r'Photon Deflection Angle $\theta$ (arcsec)', fontsize=11, fontweight='bold')
ax1.set_title(r'(a) Impact Parameter Independence of Photon Deflection', fontsize=12, fontweight='bold')
ax1.set_ylim(0.001, 5000)  # Corrected Y-limits to prevent clipping
ax1.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9)
ax1.grid(True, which='both', linestyle=':', alpha=0.6)

# --- Panel (b): Strong Lensing Benchmark Alignment ---
M_bar_range = np.logspace(10, 15, 300)
d_geom_avg_gal = 0.658
d_geom_avg_clus = 0.430

theta_E_theory_gal = np.array([(compute_theta_VSS_analytical(m, a_crit) * d_geom_avg_gal * rad_to_arcsec) for m in M_bar_range])
theta_E_theory_clus = np.array([(compute_theta_VSS_analytical(m, a_crit) * d_geom_avg_clus * rad_to_arcsec) for m in M_bar_range])

ax2.loglog(M_bar_range, theta_E_theory_gal, color='#2b8a3e', linewidth=2.0, linestyle='-.', label=r'VSS Galaxy Geometry ($d_{\mathrm{geom}} \approx 0.66$)')
ax2.loglog(M_bar_range, theta_E_theory_clus, color='#004080', linewidth=2.5, label=r'VSS Cluster Geometry ($d_{\mathrm{geom}} \approx 0.43$)')

for lens in lensing_benchmarks:
    ax2.errorbar(lens['M_bar'], lens['theta_obs'], yerr=lens['theta_err'], fmt='s', color='#d9534f', ecolor='#d9534f', capsize=4, markersize=7)
    ax2.annotate(lens['name'], (lens['M_bar'], lens['theta_obs']), textcoords="offset points", xytext=(8, -4), ha='left', fontsize=9, fontweight='bold')

ax2.set_xlabel(r'Total Baryonic Mass $M_{\mathrm{bar}}$ ($M_{\odot}$)', fontsize=11, fontweight='bold')
ax2.set_ylabel(r'Einstein Radius $\theta_E$ (arcsec)', fontsize=11, fontweight='bold')
ax2.set_title(r'(b) Strong Lensing Benchmark Alignment ($\theta_E \propto \sqrt{M_{\mathrm{bar}}}$)', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', frameon=True, facecolor='white', framealpha=0.9)
ax2.grid(True, which='both', linestyle=':', alpha=0.6)

plt.suptitle(r'Figure 5.1: Cosmological Gravitational Lensing and Deflection Angle Verification', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()

plt.savefig('figure_5_1_lensing_benchmark.png', dpi=300)
print("[SUCCESS] Regenerated 'figure_5_1_lensing_benchmark.png' with unclipped Panel (a).")
