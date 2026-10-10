import numpy as np
import matplotlib.pyplot as plt
from scipy.special import i0, i1, k0, k1

# Global publication formatting
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.family': 'sans-serif',
    'figure.autolayout': True,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'legend.fontsize': 9,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# -------------------------------------------------------------------------
# 1. Fundamental Constants (Exact SI Units)
# -------------------------------------------------------------------------
G_N = 6.67430e-11            # m^3 kg^-1 s^-2
M_sun = 1.98847e30          # kg
kpc_to_m = 3.08567758128e19  # m
c = 2.99792458e8            # m/s
H_0_SI = 2.1843e-18         # s^-1 (67.4 km/s/Mpc)

# Axiomatic Screening Gate (Zero Free Parameters)
a_crit_VSS = (c * H_0_SI) / (2.0 * np.pi)  # 1.04217e-10 m/s^2
a_0_MOND   = 1.20e-10                      # Empirical MOND parameter

# -------------------------------------------------------------------------
# 2. First-Principles Field Acceleration Routines
# -------------------------------------------------------------------------
def g_N_thin_disk(r_m, M_d, R_d_m):
    """Exact 2D Poisson Green's function solution for exponential disk."""
    y = r_m / (2.0 * R_d_m)
    return (G_N * M_d / (R_d_m**2)) * y * (i0(y)*k0(y) - i1(y)*k1(y))

def force_reduction_thick(r_m, R_d_m, z_0_m):
    """Midplane force reduction factor due to isothermal z-thickness."""
    y = r_m / R_d_m
    q0 = z_0_m / R_d_m
    return 1.0 / (1.0 + (q0 / (2.0 * y + 0.3)))

def g_baryon_total(r_m, M_star, R_star, z_0, M_gas, R_gas):
    """Total bare Newtonian acceleration (Thick Stellar + Gas Disks)."""
    g_star_thin = g_N_thin_disk(r_m, M_star, R_star)
    F_z = force_reduction_thick(r_m, R_star, z_0)
    g_star_thick = g_star_thin * F_z
    g_gas = g_N_thin_disk(r_m, M_gas, R_gas)
    return g_star_thick + g_gas

def g_NFW_cosmological(r_m, M_200, c_200):
    """NFW Dark Matter Halo Acceleration."""
    rho_crit = 3.0 * (H_0_SI**2) / (8.0 * np.pi * G_N)
    r_200 = (M_200 / ((4.0/3.0) * np.pi * 200.0 * rho_crit))**(1.0/3.0)
    r_s = r_200 / c_200
    x = r_m / r_s
    
    gc = G_N * M_200 / (r_m**2)
    f_x = np.log(1.0 + x) - (x / (1.0 + x))
    f_c = np.log(1.0 + c_200) - (c_200 / (1.0 + c_200))
    return gc * (f_x / f_c)

def g_VSS_local(g_bar):
    """Local Strain Interpolator nu(Y)."""
    Y = g_bar / a_crit_VSS
    nu = 0.5 + 0.5 * np.sqrt(1.0 + 4.0 / Y)
    return g_bar * nu

def g_MOND_standard(g_bar):
    """Standard MOND Interpolating Function."""
    return np.sqrt((g_bar**2 + np.sqrt(g_bar**4 + 4.0 * (g_bar**2) * (a_0_MOND**2))) / 2.0)

# -------------------------------------------------------------------------
# 3. System Configurations (Un-fudged Physics Parameters)
# -------------------------------------------------------------------------
# HSB Spiral Galaxy
M_star_HSB, R_star_HSB, z_0_HSB = 4.0e10 * M_sun, 3.0 * kpc_to_m, 0.6 * kpc_to_m
M_gas_HSB,  R_gas_HSB           = 1.0e10 * M_sun, 6.0 * kpc_to_m
M200_HSB,   c200_HSB            = 8.0e11 * M_sun, 10.0

# LSB Dwarf Galaxy
M_star_LSB, R_star_LSB, z_0_LSB = 8.0e7 * M_sun, 1.0 * kpc_to_m, 0.2 * kpc_to_m
M_gas_LSB,  R_gas_LSB           = 2.0e7 * M_sun, 2.0 * kpc_to_m
M200_LSB,   c200_LSB            = 3.0e9 * M_sun, 12.0

# -------------------------------------------------------------------------
# 4. Evaluation Grids & Physical Calculations
# -------------------------------------------------------------------------
r_hsb_kpc = np.linspace(0.1, 50.0, 500)
r_hsb_m = r_hsb_kpc * kpc_to_m

r_lsb_kpc = np.geomspace(0.01, 10.0, 500)  # Logarithmic grid for sub-kpc core
r_lsb_m = r_lsb_kpc * kpc_to_m

# HSB Velocities
g_bar_hsb = g_baryon_total(r_hsb_m, M_star_HSB, R_star_HSB, z_0_HSB, M_gas_HSB, R_gas_HSB)
v_bare_hsb = np.sqrt(r_hsb_m * g_bar_hsb) / 1000.0
v_lcdm_hsb = np.sqrt(r_hsb_m * (g_bar_hsb + g_NFW_cosmological(r_hsb_m, M200_HSB, c200_HSB))) / 1000.0
v_mond_hsb = np.sqrt(r_hsb_m * g_MOND_standard(g_bar_hsb)) / 1000.0
v_vss_hsb  = np.sqrt(r_hsb_m * g_VSS_local(g_bar_hsb)) / 1000.0

# LSB Velocities
g_bar_lsb = g_baryon_total(r_lsb_m, M_star_LSB, R_star_LSB, z_0_LSB, M_gas_LSB, R_gas_LSB)
v_bare_lsb = np.sqrt(r_lsb_m * g_bar_lsb) / 1000.0
v_lcdm_lsb = np.sqrt(r_lsb_m * (g_bar_lsb + g_NFW_cosmological(r_lsb_m, M200_LSB, c200_LSB))) / 1000.0
v_vss_lsb  = np.sqrt(r_lsb_m * g_VSS_local(g_bar_lsb)) / 1000.0

# Unified Acceleration Arrays
g_bar_unified = np.sort(np.concatenate([g_bar_hsb, g_bar_lsb]))
g_obs_vss_unified = g_VSS_local(g_bar_unified)
g_obs_lcdm_hsb = g_bar_hsb + g_NFW_cosmological(r_hsb_m, M200_HSB, c200_HSB)
g_obs_lcdm_lsb = g_bar_lsb + g_NFW_cosmological(r_lsb_m, M200_LSB, c200_LSB)

# Metric Slip via Bessel Green's Function
r_slip_kpc = np.linspace(0.1, 100.0, 500)
R_screen_kpc = 15.0
x_bessel = r_slip_kpc / R_screen_kpc
eta_exact = 1.0 + 0.40 * k0(x_bessel) / k0(0.1 / R_screen_kpc)

# -------------------------------------------------------------------------
# 5. Export 4 Individual Image Files
# -------------------------------------------------------------------------

# File 1: HSB Disk Rotation Curve
fig1, ax1 = plt.subplots(figsize=(7, 5))
ax1.plot(r_hsb_kpc, v_bare_hsb, 'k--', label='Bare Newtonian (Baryons Only)')
ax1.plot(r_hsb_kpc, v_lcdm_hsb, 'g-.', label=r'$\Lambda$CDM ($M_{200}=8\times10^{11} M_\odot$)')
ax1.plot(r_hsb_kpc, v_mond_hsb, 'c:', label=r'MOND ($a_0=1.2\times10^{-10}$ m/s$^2$)')
ax1.plot(r_hsb_kpc, v_vss_hsb,  'b-',  lw=2, label=r'VSS Raw Un-smoothed ($a_{crit}$)')
ax1.axhline(((G_N * (M_star_HSB + M_gas_HSB) * a_crit_VSS)**0.25)/1000.0, color='r', linestyle=':', label='BTFR Asymptote Limit')
ax1.set_xlabel('Radius r [kpc]')
ax1.set_ylabel('Circular Velocity v [km/s]')
ax1.set_title('Figure 24.1: HSB Disk Rotation Curve (Un-fudged Field Prediction)')
ax1.grid(True, alpha=0.3)
ax1.legend()
fig1.savefig('fig_24_1_hsb_disk_rotation_curve.png')
plt.close(fig1)

# File 2: LSB Dwarf Core Dynamics
fig2, ax2 = plt.subplots(figsize=(7, 5))
ax2.loglog(r_lsb_kpc, v_bare_lsb, 'k--', label='Bare Newtonian')
ax2.loglog(r_lsb_kpc, v_lcdm_lsb, 'g-.', label=r'$\Lambda$CDM NFW Cusp ($M_{200}=3\times10^9 M_\odot$)')
ax2.loglog(r_lsb_kpc, v_vss_lsb,  'b-',  lw=2, label=r'VSS Core Resolution ($v \propto r^{3/4}$)')
ax2.set_xlabel('Log Radius r [kpc]')
ax2.set_ylabel('Log Circular Velocity v [km/s]')
ax2.set_title('Figure 24.2: LSB Dwarf Core Dynamics (Logarithmic Sub-kpc Audit)')
ax2.grid(True, which="both", alpha=0.3)
ax2.legend()
fig2.savefig('fig_24_2_lsb_dwarf_core_dynamics.png')
plt.close(fig2)

# File 3: Radial Acceleration Relation (RAR)
idx_peak_lsb = np.argmax(g_bar_lsb)
g_bar_lsb_outer = g_bar_lsb[idx_peak_lsb:]
g_obs_lcdm_lsb_outer = g_obs_lcdm_lsb[idx_peak_lsb:]
g_bar_lsb_inner = g_bar_lsb[:idx_peak_lsb]
g_obs_lcdm_lsb_inner = g_obs_lcdm_lsb[:idx_peak_lsb]

fig3, ax3 = plt.subplots(figsize=(7, 5))
ax3.plot(np.log10(g_bar_unified), np.log10(g_bar_unified), 'k--', label='Newtonian 1:1 Line')
ax3.plot(np.log10(g_bar_hsb), np.log10(g_obs_lcdm_hsb), 'g-.', label=r'$\Lambda$CDM HSB Curve')
ax3.plot(np.log10(g_bar_lsb_outer), np.log10(g_obs_lcdm_lsb_outer), 'm-.', lw=1.5, label=r'$\Lambda$CDM LSB Outer Disk')
ax3.plot(np.log10(g_bar_lsb_inner), np.log10(g_obs_lcdm_lsb_inner), 'm:', lw=1.2, alpha=0.7, label=r'$\Lambda$CDM LSB Inner Core Trace')
ax3.plot(np.log10(g_bar_unified), np.log10(g_obs_vss_unified), 'b-', lw=2, label='VSS Universal RAR Curve')
ax3.axvline(np.log10(a_crit_VSS), color='r', linestyle=':', label=r'$a_{crit}$ Gate')
ax3.set_xlabel(r'$\log_{10}( g_{bar} $ [m/s$^2$] $)$')
ax3.set_ylabel(r'$\log_{10}( g_{obs} $ [m/s$^2$] $)$')
ax3.set_title('Figure 24.3: Radial Acceleration Relation (Full Domain Audit)')
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=8)
fig3.savefig('fig_24_3_radial_acceleration_relation.png')
plt.close(fig3)

# File 4: Quasi-Linear Metric Slip
fig4, ax4 = plt.subplots(figsize=(7, 5))
ax4.plot(r_slip_kpc, eta_exact, 'b-', lw=2, label=r'VSS Exact Propagator $\eta(r) = 1 + \mu_0 K_0(r/R_s)$')
ax4.axhline(1.0, color='r', linestyle='--', label=r'GR Limit ($\eta = 1.00$)')
ax4.set_xlabel('Scale Radius r [kpc]')
ax4.set_ylabel(r'Metric Slip $\eta \equiv \Phi / \Psi$')
ax4.set_title('Figure 24.4: Quasi-Linear Metric Slip (Exact Green Function)')
ax4.grid(True, alpha=0.3)
ax4.legend()
fig4.savefig('fig_24_4_quasilinear_metric_slip.png')
plt.close(fig4)

print("Saved 4 individual PNG image files successfully.")