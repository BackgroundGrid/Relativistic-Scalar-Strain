#!/usr/bin/env python3
"""
VSS/RSS Monograph Series - Volume III
Section 22: Intracluster Plasma Hydrostatics & Thermal/Kinematic SZ Effect
File: section_22_sunyaev_zeldovich.py

Description:
  Executes first-principles hydrostatic integration for high-temperature 
  intracluster gas (T_e ~ 10^7 - 10^8 K) under Screened VSS, LCDM NFW benchmark, 
  and Pure GR. Includes non-thermal turbulent pressure support P_nth(r), 
  thermal Compton y-parameter profiles y(R), and Thomson optical depth tau_e(R).
  Execution time: < 3 seconds.
"""

import numpy as np
from scipy.integrate import quad, cumulative_trapezoid
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

# ==============================================================================
# 1. PHYSICAL CONSTANTS (SI UNITS)
# ==============================================================================
M_SUN_KG = 1.98847e30           # Solar mass [kg]
MPC_TO_M = 3.08567758149137e22   # Megaparsec [m]
G_SI = 6.67430e-11              # Gravitational constant [m^3 kg^-1 s^-2]
C_SI = 2.99792458e8             # Speed of light [m/s]
K_B_SI = 1.380649e-23           # Boltzmann constant [J/K]
M_P_SI = 1.67262192e-27         # Proton mass [kg]
M_E_SI = 9.10938370e-31         # Electron mass [kg]
SIGMA_T_SI = 6.65245873e-29     # Thomson cross-section [m^2]
KEV_TO_K = 1.160451812e7        # 1 keV in Kelvin

# Plasma Mean Molecular Mass Constants
MU = 0.60                       # Mean molecular weight per particle
MU_E = 1.14                     # Mean molecular weight per free electron

# Monograph Acceleration Gate Scale
A_CRIT = 1.042e-10              # a_crit = c * H_0 / (2 * pi) [m/s^2]

# Cluster Scale Parameters
M_TOT_BAR_MSUN = 1.5e14         # Total baryonic mass [M_sun]
R_CORE_MPC = 0.10               # Core radius [Mpc]
R_200_MPC = 1.80                # Cosmological screening boundary [Mpc]

# Gas Fraction Parameters (Modified beta-model gas density)
R_GAS_C_MPC = 0.15              # Gas core radius [Mpc]
BETA_GAS = 0.67                 # Beta model slope exponent
RHO_0_GAS_KG_M3 = 3.5e-23       # Central gas density ~ 0.012 cm^-3 [kg/m^3]

# ==============================================================================
# 2. DENSITY & ACCELERATION FUNCTIONS
# ==============================================================================
def rho_gas_kg_m3(r_mpc):
    """3D Gas density profile [kg/m^3]"""
    return RHO_0_GAS_KG_M3 * (1.0 + (r_mpc / R_GAS_C_MPC)**2)**(-1.5 * BETA_GAS)

def M_bar_kg(r_mpc):
    """Total enclosed baryonic mass [kg]"""
    m_msun = M_TOT_BAR_MSUN * (r_mpc**2) / ((r_mpc + R_CORE_MPC)**2)
    return m_msun * M_SUN_KG

def g_N_si(r_mpc):
    """Newtonian baryonic acceleration [m/s^2]"""
    r_m = r_mpc * MPC_TO_M
    return (G_SI * M_bar_kg(r_mpc)) / (r_m**2)

def nu_vss(y):
    """Universal strain interpolating function"""
    return 0.5 + 0.5 * np.sqrt(1.0 + 4.0 / y)

def g_eff_vss_si(r_mpc):
    """Screened VSS effective acceleration field [m/s^2]"""
    g_val = g_N_si(r_mpc)
    y_val = g_val / A_CRIT
    nu_raw = nu_vss(y_val)
    screening = 1.0 / (1.0 + (r_mpc / R_200_MPC)**2)
    nu_screened = 1.0 + (nu_raw - 1.0) * screening
    return g_val * nu_screened

def g_eff_nfw_si(r_mpc):
    """LCDM NFW Dark Matter Benchmark Acceleration Field [m/s^2]"""
    M_200_kg = 8.0e14 * M_SUN_KG
    c_nfw = 4.0
    r_s_mpc = R_200_MPC / c_nfw
    x = r_mpc / r_s_mpc
    
    # Enclosed NFW mass profile
    fc = np.log(1.0 + c_nfw) - c_nfw / (1.0 + c_nfw)
    fx = np.log(1.0 + x) - x / (1.0 + x)
    M_nfw_encl = M_200_kg * (fx / fc)
    
    r_m = r_mpc * MPC_TO_M
    return (G_SI * (M_nfw_encl + M_bar_kg(r_mpc))) / (r_m**2)

# ==============================================================================
# 3. HYDROSTATIC TEMPERATURE & NON-THERMAL PRESSURE PIPELINE
# ==============================================================================
def compute_hydrostatic_temperature(g_eff_func, r_grid_mpc):
    r"""
    Computes T_e(r) [K] via outward integral of hydrostatic pressure:
    P_gas(r) = \int_r^r_max \rho_gas(r') g_eff(r') dr'
    """
    r_fine = np.logspace(-2, 1.3, 1200) # 0.01 Mpc to 20.0 Mpc
    r_fine_m = r_fine * MPC_TO_M
    rho_fine = rho_gas_kg_m3(r_fine)
    g_fine = np.array([g_eff_func(r) for r in r_fine])
    
    integrand = rho_fine * g_fine
    
    # Forward cumulative integration: \int_r^{r_max} = \int_0^{r_max} - \int_0^r
    P_cum = cumulative_trapezoid(integrand, r_fine_m, initial=0.0)
    pressure_fine = P_cum[-1] - P_cum
    
    # T_e(r) = (mu * m_p / k_B) * (P_gas / rho_gas)
    T_fine = (MU * M_P_SI / K_B_SI) * (pressure_fine / rho_fine)
    
    f_T = interp1d(r_fine, T_fine, kind='cubic', bounds_error=False, fill_value=0.0)
    return f_T(r_grid_mpc)

def compute_vss_non_thermal_pressure_and_temp(r_grid_mpc):
    r"""
    Computes thermal temperature corrected for VSS strain-induced non-thermal 
    turbulent pressure support: P_tot = P_th + P_nth
    """
    T_tot_K = compute_hydrostatic_temperature(g_eff_vss_si, r_grid_mpc)
    
    g_eff = np.array([g_eff_vss_si(r) for r in r_grid_mpc])
    g_N   = np.array([g_N_si(r) for r in r_grid_mpc])
    r_m   = r_grid_mpc * MPC_TO_M
    
    # Strain-driven turbulent velocity dispersion sigma_turb^2 = r * (g_eff - g_N)
    sigma_turb_sq = r_m * np.maximum(0.0, g_eff - g_N)
    
    # Thermal Temperature T_th = T_tot - (mu * m_p / (3 * k_B)) * sigma_turb^2
    T_th_K = T_tot_K - (MU * M_P_SI / (3.0 * K_B_SI)) * sigma_turb_sq
    T_th_K = np.maximum(T_th_K, 0.1 * T_tot_K) # Physical thermal floor
    
    P_nth_ratio = (MU * M_P_SI * sigma_turb_sq / (3.0 * K_B_SI)) / T_tot_K
    
    return T_th_K, P_nth_ratio

# ==============================================================================
# 4. COMPTON Y-PARAMETER & OPTICAL DEPTH LINE-OF-SIGHT INTEGRATION
# ==============================================================================
def compute_compton_y_profile(T_e_func, R_grid_mpc):
    r"""
    Computes y(R) = (2 * sigma_T * k_B / m_e c^2) * \int_0^u_max n_e(r) T_e(r) du
    where r = sqrt(R^2 + u^2)
    """
    prefactor = (2.0 * SIGMA_T_SI * K_B_SI) / (M_E_SI * C_SI**2)
    y_profile = np.zeros_like(R_grid_mpc)
    
    for i, R_val in enumerate(R_grid_mpc):
        def integrand(u_mpc):
            r_mpc = np.sqrt(R_val**2 + u_mpc**2)
            rho_g = rho_gas_kg_m3(r_mpc)
            n_e = rho_g / (MU_E * M_P_SI)
            T_val = T_e_func(r_mpc)
            return n_e * T_val
        
        integral_val, _ = quad(integrand, 0.0, 10.0, limit=100)
        integral_val_m = integral_val * MPC_TO_M
        y_profile[i] = prefactor * integral_val_m
        
    return y_profile

def compute_thomson_optical_depth_tau(R_grid_mpc):
    r"""
    Computes cluster optical depth profile tau_e(R) for kSZ signal
    tau_e(R) = (2 * sigma_T / (mu_e * m_p)) * \int_0^u_max rho_gas(sqrt(R^2 + u^2)) du
    """
    prefactor = (2.0 * SIGMA_T_SI) / (MU_E * M_P_SI)
    tau_profile = np.zeros_like(R_grid_mpc)
    
    for i, R_val in enumerate(R_grid_mpc):
        def integrand(u_mpc):
            r_mpc = np.sqrt(R_val**2 + u_mpc**2)
            return rho_gas_kg_m3(r_mpc)
        
        integral_val, _ = quad(integrand, 0.0, 10.0, limit=100)
        tau_profile[i] = prefactor * (integral_val * MPC_TO_M)
        
    return tau_profile

# ==============================================================================
# 5. EXECUTION & VISUAL GENERATION
# ==============================================================================
if __name__ == "__main__":
    r_plot_mpc = np.logspace(-1, 0.6, 60) # 0.1 Mpc to 4.0 Mpc
    
    # 1. Compute Hydrostatic Temperatures
    T_vss_K = compute_hydrostatic_temperature(g_eff_vss_si, r_plot_mpc)
    T_vss_th_K, P_nth_ratio = compute_vss_non_thermal_pressure_and_temp(r_plot_mpc)
    T_nfw_K = compute_hydrostatic_temperature(g_eff_nfw_si, r_plot_mpc)
    T_gr_K  = compute_hydrostatic_temperature(g_N_si, r_plot_mpc)
    
    # Convert to keV
    T_vss_keV    = T_vss_K / KEV_TO_K
    T_vss_th_keV = T_vss_th_K / KEV_TO_K
    T_nfw_keV    = T_nfw_K / KEV_TO_K
    T_gr_keV     = T_gr_K / KEV_TO_K
    
    # 2. Interpolators for Projection Integrals (Extended domain up to 15.85 Mpc)
    r_interp_mpc = np.logspace(-2, 1.2, 300)
    T_vss_interp = interp1d(r_interp_mpc, compute_hydrostatic_temperature(g_eff_vss_si, r_interp_mpc), kind='cubic', bounds_error=False, fill_value=0.0)
    T_nfw_interp = interp1d(r_interp_mpc, compute_hydrostatic_temperature(g_eff_nfw_si, r_interp_mpc), kind='cubic', bounds_error=False, fill_value=0.0)
    T_gr_interp  = interp1d(r_interp_mpc, compute_hydrostatic_temperature(g_N_si, r_interp_mpc), kind='cubic', bounds_error=False, fill_value=0.0)
    
    # 3. Compute Compton y-Profiles & Optical Depth tau_e(R)
    y_vss = compute_compton_y_profile(T_vss_interp, r_plot_mpc)
    y_nfw = compute_compton_y_profile(T_nfw_interp, r_plot_mpc)
    y_gr  = compute_compton_y_profile(T_gr_interp, r_plot_mpc)
    tau_e = compute_thomson_optical_depth_tau(r_plot_mpc)
    
    # 4. Render Two-Panel Monograph Figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    # Left Panel: Plasma Temperature & Non-Thermal Support
    ax1.semilogx(r_plot_mpc, T_vss_keV, 'b-', lw=2.5, label='VSS Total Gas Temp $T_{tot}$')
    ax1.semilogx(r_plot_mpc, T_vss_th_keV, 'c--', lw=2.0, label='VSS Thermal Temp $T_{th}$ ($P_{th} = P_{tot}-P_{nth}$)')
    ax1.semilogx(r_plot_mpc, T_nfw_keV, 'k--', lw=1.8, label=r'$\Lambda$CDM NFW DM Benchmark')
    ax1.semilogx(r_plot_mpc, T_gr_keV, 'r:', lw=1.8, label='Pure GR (Baryons Only)')
    ax1.axvline(R_200_MPC, color='gray', linestyle='--', label=r'Screening Boundary $R_{200}$')
    ax1.set_xlabel('Physical Radius $r$ [Mpc]', fontsize=12)
    ax1.set_ylabel(r'Gas Temperature $k_B T_e$ [keV]', fontsize=12)
    ax1.set_title('Intracluster Gas Hydrostatic Temperature', fontsize=13, fontweight='bold')
    ax1.set_ylim(0.0, 10.0)
    ax1.grid(True, which="both", ls="--", alpha=0.5)
    ax1.legend(fontsize=9, loc='upper right')
    
    # Right Panel: Thermal SZ (y) & Thomson Optical Depth (tau_e)
    ax2.loglog(r_plot_mpc, y_vss, 'b-', lw=2.5, label='VSS Thermal SZ $y(R)$')
    ax2.loglog(r_plot_mpc, y_nfw, 'k--', lw=1.8, label=r'$\Lambda$CDM NFW SZ Benchmark')
    ax2.loglog(r_plot_mpc, y_gr, 'r:', lw=1.8, label='Pure GR SZ (Baryons Only)')
    ax2.loglog(r_plot_mpc, tau_e * 1e-1, 'm-.', lw=1.8, label=r'VSS Optical Depth $\tau_e(R) \times 10^{-1}$')
    ax2.set_xlabel('Projected Radius $R$ [Mpc]', fontsize=12)
    ax2.set_ylabel(r'Compton $y$-Parameter / Optical Depth $\tau_e$', fontsize=12)
    ax2.set_title('SZ Projection & kSZ Optical Depth Profiles', fontsize=13, fontweight='bold')
    ax2.set_ylim(1e-6, 1e-3)
    ax2.grid(True, which="both", ls="--", alpha=0.5)
    ax2.legend(fontsize=9, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('section_22_sunyaev_zeldovich.png')
    print("Execution complete. Updated figure saved to 'section_22_sunyaev_zeldovich.png'")