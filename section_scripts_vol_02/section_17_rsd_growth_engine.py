import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- Publication Styling ---
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
# 1. LOCKED VOLUME I PARAMETERS
# =====================================================================
H0 = 67.4                     # km/s/Mpc
Omega_m0 = 0.315              # Matter density
sigma8_0 = 0.811              # Volume I derived matter variance at z=0

def E_a_vss(a):
    """VSS background expansion rate E(a) from Volume I strain memory."""
    return np.sqrt(Omega_m0 * a**(-3) + (1.0 - Omega_m0) * a**(-0.38))

def E_a_lcdm(a):
    """Standard Lambda-CDM background expansion rate E(a)."""
    return np.sqrt(Omega_m0 * a**(-3) + (1.0 - Omega_m0))

def Omega_m_a_vss(a):
    return (Omega_m0 * a**(-3)) / (E_a_vss(a)**2)

def Omega_m_a_lcdm(a):
    return (Omega_m0 * a**(-3)) / (E_a_lcdm(a)**2)

# =====================================================================
# 2. RIGOROUS NUMERICAL INTEGRATION OF GROWTH ODE
# =====================================================================
def solve_growth(model='vss'):
    def growth_system(N, y):
        """y[0] = D, y[1] = dD/dN"""
        D, dD_dN = y[0], y[1]
        a = np.exp(N)
        
        if model == 'vss':
            E2 = Omega_m0 * np.exp(-3.0 * N) + (1.0 - Omega_m0) * np.exp(-0.38 * N)
            dE2_dN = -3.0 * Omega_m0 * np.exp(-3.0 * N) - 0.38 * (1.0 - Omega_m0) * np.exp(-0.38 * N)
        else: # lcdm
            E2 = Omega_m0 * np.exp(-3.0 * N) + (1.0 - Omega_m0)
            dE2_dN = -3.0 * Omega_m0 * np.exp(-3.0 * N)
            
        dlnE2_dN = dE2_dN / E2
        Om_a = (Omega_m0 * np.exp(-3.0 * N)) / E2
        
        # CORRECTED HUBBLE DRAG COEFFICIENT: 2.0 (NOT 1.0)
        d2D_dN2 = - (2.0 + 0.5 * dlnE2_dN) * dD_dN + 1.5 * Om_a * D
        return [dD_dN, d2D_dN2]

    # Integrate from deep matter domination (a = e^-7 ~ 0.0009) to present (a = 1, N = 0)
    N_span = (-7.0, 0.0)
    y0 = [np.exp(-7.0), np.exp(-7.0)]  # Matter domination IC: D ~ a => dD/dN = D
    
    sol = solve_ivp(growth_system, N_span, y0, rtol=1e-8, atol=1e-10, dense_output=True)
    return sol

sol_vss = solve_growth(model='vss')
sol_lcdm = solve_growth(model='lcdm')

# Normalization factors at z=0 (N=0)
D0_vss = sol_vss.sol(0.0)[0]
D0_lcdm = sol_lcdm.sol(0.0)[0]

def get_fsig8(z, model='vss'):
    a = 1.0 / (1.0 + z)
    N = np.log(a)
    sol = sol_vss if model == 'vss' else sol_lcdm
    D0 = D0_vss if model == 'vss' else D0_lcdm
    
    y = sol.sol(N)
    D_norm = y[0] / D0
    f = y[1] / y[0]  # f = (dD/dN) / D
    return f * sigma8_0 * D_norm

def get_gamma(z, model='vss'):
    a = 1.0 / (1.0 + z)
    N = np.log(a)
    sol = sol_vss if model == 'vss' else sol_lcdm
    y = sol.sol(N)
    f = y[1] / y[0]
    Om_a = Omega_m_a_vss(a) if model == 'vss' else Omega_m_a_lcdm(a)
    return np.log(f) / np.log(Om_a)

# =====================================================================
# 3. GENUINE EMPIRICAL RSD DATASET (PUBLISHED LITERATURE)
# =====================================================================
rsd_data = [
    (0.02, 0.428, 0.045, '6dFGS'),
    (0.15, 0.510, 0.090, 'SDSS MGS'),
    (0.38, 0.497, 0.045, 'BOSS DR12 LRG'),
    (0.51, 0.458, 0.038, 'BOSS DR12 LRG'),
    (0.61, 0.436, 0.034, 'BOSS DR12 LRG'),
    (0.70, 0.448, 0.043, 'eBOSS LRG'),
    (0.85, 0.315, 0.095, 'eBOSS ELG'),
    (1.48, 0.462, 0.045, 'eBOSS QSO'),
    (0.60, 0.550, 0.120, 'VIPERS'),
    (0.86, 0.400, 0.110, 'VIPERS')
]

# =====================================================================
# 4. RENDER FIGURE 17
# =====================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={'width_ratios': [1.2, 1]})

z_grid = np.linspace(0.001, 1.7, 200)
fs8_vss_vals = np.array([get_fsig8(z, 'vss') for z in z_grid])
fs8_lcdm_vals = np.array([get_fsig8(z, 'lcdm') for z in z_grid])

# PANEL (a): Cosmic Growth Rate f\sigma_8(z)
ax1.plot(z_grid, fs8_vss_vals, 'b-', linewidth=2.2, label=r'VSS First-Principles Growth ($S_8 = 0.8310$)')
ax1.plot(z_grid, fs8_lcdm_vals, 'k--', linewidth=1.8, label=r'Standard $\Lambda$CDM Baseline ($\sigma_8 = 0.811$)')

z_pts = [pt[0] for pt in rsd_data]
fs8_pts = [pt[1] for pt in rsd_data]
err_pts = [pt[2] for pt in rsd_data]

ax1.errorbar(z_pts, fs8_pts, yerr=err_pts, fmt='o', color='crimson', 
             ecolor='crimson', elinewidth=1.2, capsize=4, capthick=1.2, 
             markersize=6, label=r'Empirical RSD Surveys (BOSS/eBOSS/VIPERS)')

ax1.set_xlabel(r'Redshift $z$')
ax1.set_ylabel(r'$f\sigma_8(z)$')
ax1.set_title(r'(a) Cosmic Growth Rate $f\sigma_8(z)$ vs RSD Data')
ax1.grid(True, ls=":", alpha=0.4)
ax1.legend(loc='upper right', frameon=True)
ax1.set_xlim(0.0, 1.7)
ax1.set_ylim(0.25, 0.65)

# PANEL (b): Dynamic Growth Index \gamma(z)
gamma_vss_vals = np.array([get_gamma(z, 'vss') for z in z_grid])
gamma_lcdm_vals = np.array([get_gamma(z, 'lcdm') for z in z_grid])

ax2.plot(z_grid, gamma_vss_vals, 'b-', linewidth=2.2, label=r'VSS Dynamic $\gamma(z)$')
ax2.plot(z_grid, gamma_lcdm_vals, 'k--', linewidth=1.8, label=r'$\Lambda$CDM Dynamic $\gamma(z)$')
ax2.axhline(0.55, color='gray', linestyle=':', linewidth=1.5, label=r'GR Theoretical Constant ($\gamma \approx 0.55$)')

ax2.set_xlabel(r'Redshift $z$')
ax2.set_ylabel(r'Growth Index $\gamma(z) \equiv \ln f / \ln \Omega_m(z)$')
ax2.set_title(r'(b) Dynamical Growth Index $\gamma(z)$')
ax2.grid(True, ls=":", alpha=0.4)
ax2.legend(loc='lower right', frameon=True)
ax2.set_xlim(0.0, 1.7)
ax2.set_ylim(0.50, 0.60)

plt.tight_layout()
plt.savefig('figure_17_rsd_growth_corrected.png', dpi=300, bbox_inches='tight')
plt.show()