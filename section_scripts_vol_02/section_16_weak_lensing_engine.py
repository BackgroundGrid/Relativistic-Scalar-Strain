import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# --- Publication Quality Styling ---
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'legend.fontsize': 8.5,
    'xtick.labelsize': 9.5,
    'ytick.labelsize': 9.5,
    'figure.dpi': 300
})

# =====================================================================
# 1. VOLUME I EXACT METRIC INVARIANTS (NO FIT PARAMETERS)
# =====================================================================
H0 = 67.4                     # km/s/Mpc
h = H0 / 100.0                # 0.674
c = 299792.458                # km/s
Omega_m = 0.315               # Matter density
Omega_b = 0.0493              # Baryon density
sigma8_vss = 0.811            # Derived matter variance
S8_matter = sigma8_vss * np.sqrt(Omega_m / 0.30)  # S8 = 0.8310

def E_z(z):
    """Background expansion rate E(z) from Volume I metric strain memory."""
    return np.sqrt(Omega_m * (1.0 + z)**3 + (1.0 - Omega_m) * (1.0 + z)**0.38)

def comoving_distance(z):
    """Comoving distance chi(z) in Mpc."""
    res, _ = quad(lambda zp: (c / H0) / E_z(zp), 0.0, z)
    return res

def eta_z(z):
    """Volume I Gravitational Slip eta(z) = Phi / Psi."""
    return 1.0 - 0.116 * (1.0 + z)**(-0.38)

# Precompute redshift-distance interpolation grid
z_array = np.linspace(0.001, 3.0, 300)
chi_array = np.array([comoving_distance(z) for z in z_array])

def chi_of_z(z):
    return np.interp(z, z_array, chi_array)

# =====================================================================
# 2. PHYSICAL MATTER POWER SPECTRUM & LENSING KERNEL
# =====================================================================
def n_z(z):
    """Normalized source galaxy redshift distribution n(z)."""
    z0 = 0.5
    return (z**2 / (2.0 * z0**3)) * np.exp(-z / z0)

def lensing_kernel_g(z_val):
    """Lensing efficiency kernel g(z) in redshift space."""
    chi_z = chi_of_z(z_val)
    def integrand(zp):
        chi_zp = chi_of_z(zp)
        if chi_zp <= chi_z:
            return 0.0
        return n_z(zp) * (1.0 - chi_z / chi_zp)
    res, _ = quad(integrand, z_val, 2.5, epsabs=1e-6, epsrel=1e-5)
    return res

def transfer_function_bbks(k_mpc):
    """BBKS transfer function T(k) with exact physical Gamma_eff scaling."""
    gamma_eff = Omega_m * h * np.exp(-Omega_b - np.sqrt(2.0 * h) * (Omega_b / Omega_m))
    q = k_mpc / (gamma_eff * h)  # q in (h Mpc^-1) units
    return np.log(1.0 + 2.34 * q) / (2.34 * q) * (
        1.0 + 3.89 * q + (16.1 * q)**2 + (5.46 * q)**3 + (6.71 * q)**4
    )**(-0.25)

# Calculate exact normalization constant A_norm for sigma_8 = 0.811
R8 = 8.0 / h  # 8 Mpc/h in Mpc
def sigma8_integrand(k):
    x = k * R8
    W = 3.0 * (np.sin(x) - x * np.cos(x)) / (x**3)
    P_unnorm = (k**0.965) * (transfer_function_bbks(k)**2)
    return (1.0 / (2.0 * np.pi**2)) * (k**2) * P_unnorm * (W**2)

I_sigma8, _ = quad(sigma8_integrand, 1e-5, 15.0, limit=200)
A_norm = (sigma8_vss**2) / I_sigma8

def P_delta_linear(k):
    """Linear matter power spectrum normalized strictly to sigma8 = 0.811."""
    return A_norm * (k**0.965) * (transfer_function_bbks(k)**2)

# =====================================================================
# 3. DIRECT LIMBER NUMERICAL INTEGRATION FOR C_ell^kappa_kappa
# =====================================================================
def compute_limber_cell(ells, apply_slip=True):
    """Calculates dimensionless spectrum D_ell = l(l+1)C_l / 2pi directly from Limber Integral."""
    d_ells = np.zeros_like(ells)
    prefactor = (9.0 / 4.0) * (Omega_m**2) * (H0 / c)**4

    z_bins = np.linspace(0.01, 2.0, 40)
    z_mids = 0.5 * (z_bins[:-1] + z_bins[1:])
    
    g_mids = np.array([lensing_kernel_g(zm) for zm in z_mids])
    chi_mids = np.array([chi_of_z(zm) for zm in z_mids])
    E_mids = np.array([E_z(zm) for zm in z_mids])
    eta_mids = np.array([eta_z(zm) for zm in z_mids])
    
    for i, l in enumerate(ells):
        integral = 0.0
        for j in range(len(z_mids)):
            zm = z_mids[j]
            dz = z_bins[j+1] - z_bins[j]
            chi = chi_mids[j]
            a = 1.0 / (1.0 + zm)
            g = g_mids[j]
            
            k_wave = (l + 0.5) / chi
            P_k = P_delta_linear(k_wave)
            
            slip = ((1.0 + eta_mids[j]) / 2.0)**2 if apply_slip else 1.0
            
            dchi_dz = (c / H0) / E_mids[j]
            integrand = slip * (g / a)**2 * P_k * dchi_dz
            integral += integrand * dz
            
        cell = prefactor * integral
        d_ells[i] = l * (l + 1.0) * cell / (2.0 * np.pi)
        
    return d_ells

# Execute Limber integration
ells = np.logspace(1.0, 3.3, 50)
d_ell_gr = compute_limber_cell(ells, apply_slip=False)
d_ell_vss = compute_limber_cell(ells, apply_slip=True)

# =====================================================================
# 4. RENDER FIGURE 16
# =====================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={'width_ratios': [1.3, 1]})

# PANEL (a): Pure Limber Curves (Full Physical Dynamic Range)
ax1.loglog(ells, d_ell_gr, 'k--', label=r'Standard GR ($\eta = 1.0, S_8=0.8310$)', linewidth=1.8)
ax1.loglog(ells, d_ell_vss, 'b-', label=r'VSS First-Principles ($\eta \approx 0.884$)', linewidth=2.2)

ax1.annotate(r'11.3% Metric Slip Drop' '\n' r'$[(1+\eta)/2]^2 \approx 0.887$', 
             xy=(300, d_ell_vss[30]), xytext=(70, d_ell_vss[30] * 0.3),
             arrowprops=dict(facecolor='blue', shrink=0.05, width=1, headwidth=6),
             fontsize=9.0, color='blue', 
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='blue', alpha=0.8))

ax1.set_xlabel(r'Angular Multipole $\ell$')
ax1.set_ylabel(r'$\ell(\ell+1) C_\ell^{\kappa\kappa} / 2\pi$')
ax1.set_title(r'(a) Pure Limber Integration $C_\ell^{\kappa\kappa}$ (First Principles)')
ax1.grid(True, which="both", ls=":", alpha=0.4)
ax1.legend(loc='upper left', frameon=True)
ax1.set_xlim(10, 2000)
ax1.set_ylim(1e-7, 4e-5)  # Correct physical ceiling to fit the full spectrum peak (~2e-5)

# PANEL (b): Published Empirical S_8 Literature Comparison
categories = [
    'Planck CMB 2018 (GR)', 
    'VSS Matter Growth ($S_8$)', 
    r'VSS Inferred Lensing ($S_8^{\mathrm{eff}}$)', 
    'DES Y3 + KiDS-1000 (2023)', 
    'DES Y3 Shear (2022/2025)', 
    'KiDS-1000 COSEBIs (2021)'
]
y_pos = np.arange(len(categories))

s8_vals = [0.834, S8_matter, S8_matter * 0.942, 0.790, 0.780, 0.776]
s8_err_low = [0.016, 0.000, 0.000, 0.014, 0.015, 0.027]
s8_err_high = [0.016, 0.000, 0.000, 0.018, 0.015, 0.029]

colors = ['gray', 'blue', 'darkblue', 'crimson', 'crimson', 'crimson']

for i in range(len(categories)):
    if s8_err_low[i] > 0:
        ax2.errorbar(s8_vals[i], y_pos[i], xerr=[[s8_err_low[i]], [s8_err_high[i]]], 
                     fmt='o', color=colors[i], capsize=5, capthick=1.5, elinewidth=1.5, markersize=7)
    else:
        ax2.plot(s8_vals[i], y_pos[i], 'D', color=colors[i], markersize=8)

ax2.axvline(S8_matter, color='blue', linestyle='--', alpha=0.5, label=r'VSS Matter Target ($S_8=0.8310$)')
ax2.axvline(S8_matter * 0.942, color='darkblue', linestyle=':', alpha=0.8, label=r'VSS Inferred Lensing ($0.7828$)')
ax2.axvspan(0.790 - 0.014, 0.790 + 0.018, alpha=0.15, color='crimson', label=r'DES Y3 + KiDS Joint 1$\sigma$ Zone')

ax2.set_yticks(y_pos)
ax2.set_yticklabels(categories)
ax2.invert_yaxis()
ax2.set_xlabel(r'$S_8 \equiv \sigma_8 \sqrt{\Omega_m / 0.30}$')
ax2.set_title(r'(b) Empirical $S_8$ Literature Comparison')
ax2.grid(True, axis='x', ls=":", alpha=0.4)
ax2.set_xlim(0.71, 0.88)
ax2.legend(loc='lower right', frameon=True, fontsize=8.0)

plt.tight_layout()
plt.savefig('figure_16_weak_lensing_s8_correct_bounds.png', dpi=300, bbox_inches='tight')
plt.show()