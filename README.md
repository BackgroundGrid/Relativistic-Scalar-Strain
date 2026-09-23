# Relativistic Scalar Strain (RSS) Architecture
## Vacuum Stress Saturation (VSS) / Vacuum Interlocking Gravity (VIG) Monograph & Simulation Suite

[![DOI Volume 1](https://zenodo.org/badge/DOI/10.5281/zenodo.22810512.svg)](https://doi.org/10.5281/zenodo.22810512)
[![DOI Volume II](https://zenodo.org/badge/DOI/10.5281/zenodo.22914793.svg)](https://doi.org/10.5281/zenodo.22914793)

> **Notice:** Proprietary research, field-theoretic derivations, numerical simulation engines, and visual proofs for the Relativistic Scalar Strain (RSS) Architecture / Vacuum Stress Saturation (VSS) framework. Copyright © 2026 Ravinder Singh. All Rights Reserved. Reproduction, redistribution, or AI model ingestion is strictly prohibited under the enclosed `License.md`.

---

## Architecture Summary

The **Relativistic Scalar Strain (RSS)** architecture—operating under the **Vacuum Stress Saturation (VSS)** engine—formulates space-time as a non-linear elastic continuum with finite strain saturation. By replacing passive vacuum assumptions with a constitutive strain boundary condition, the framework derives local astrophysical dynamics, cluster hydrostatics, cosmological growth, and large-scale observables directly from visible baryonic mass distributions with **zero free parameters**, zero halo profile fitting, and zero dark matter or dark energy fluids.

### Monograph Series Overview

* **Volume I: Local Kinematics & Astrophysical Regimes**  
  Derives the axiomatic acceleration scale $a_{\text{crit}}$, solar system screening mechanisms, SPARC galactic rotation curves, galaxy cluster hydrostatics, and local metric weak lensing.
* **Volume II: Linear Perturbation Theory & Cosmological Observables**  
  Formulates modified gauge-invariant scalar metric perturbations, linear growth factor evolution $D(z)$, the structure growth rate $f\sigma_8(z)$, cosmological metric slip $\eta(z)$, CMB temperature anisotropies $C_\ell^{TT}$, 3D matter power spectrum $P(k,z)$, BAO scales, and a parameter-free resolution to the $S_8$ weak-lensing tension.

### Core Mathematical Pillars

1. **Axiomatic Acceleration Scale:** Derived strictly from fundamental constants and spherical horizon geometry:
   $$a_{\text{crit}} \equiv \frac{c \cdot H_0}{2\pi} \approx 1.0422 \times 10^{-10}\text{ m/s}^2$$

2. **Master Constitutive Relation:** Governs gravitational response across all physical mass scales:
   $$g_{\text{obs}}\left(1 - e^{-g_{\text{obs}}/a_{\text{crit}}}\right) = g_{\text{bar}}$$

3. **Cosmological Metric Slip Ratio $\eta(z)$:** Analytical decoupling of weak-lensing potential ($\Phi + \Psi$) from non-relativistic matter growth ($\Psi$):
   $$\eta(z) \equiv \frac{\Phi}{\Psi} = 1 - 0.116(1+z)^{-0.38}$$

4. **Geometric Vacuum Saturation:** Exact horizon boundary closure replacing Dark Energy:
   $$\Omega_{\text{vac}} = 1 - \Omega_b = 1 - 0.049 = 0.951 \quad (\text{Effective background fraction})$$

---

## Repository Structure

The workspace is flattened at the root level to eliminate OS path depth limits and ensure clean multi-volume execution:

```text
├── Run_all_VI.py                            # Master orchestrator for Volume 1 pipeline
├── Run_all_VII.py                        # Master orchestrator for Volume 2 pipeline
├── equations_results.txt                 # Auto-generated standalone ledger for Volume 1
├── equations_results_VII.txt             # Auto-generated standalone ledger for Volume 2
├── requirements.txt                      # Dependency manifest (NumPy, SciPy, Matplotlib, Pytest)
├── License.md                            # Proprietary copyright notice
├── README.md                             # Monograph documentation & build guide
├── Citation.cff
├── RESEARCH_SUPPORT.md                   # Calling for Support  
│
├── section_scripts_vol_01/               # Volume I physics modules & simulation engines
│   ├── section_01_axiomatic_derivation.py
│   ├── section_02_solar_system_screening.py
│   ├── section_03_sparc_galaxies.py
│   ├── section_04_cluster_hydrostatics.py
│   ├── section_05_metric_lensing.py
│   ├── section_06_cosmological_synthesis.py
│   ├── section_07_cosmological_3d_simulation.py
│   └── equations_results.py              # Volume I disk write module for equations_results.txt
│
├── section_scripts_vol_02/               # Volume II physics engines & numerical solvers
│   ├── section_08_variational_action.py  # Field-theoretic variational action & field equations
│   ├── section_09_cluster_dynamics.py    # Cluster dynamics & non-linear potential profiles
│   ├── section_10_cosmic_expansion.py    # Background expansion rate E(z) & H(z) solver
│   ├── section_11_cmb_bao_engine.py      # Integrated CMB acoustic peak & BAO engine
│   ├── section_12_cosmic_shear_engine.py # Weak lensing cosmic shear convergence spectrum
│   ├── section_13_cmb_fixed_engine.py    # CMB temperature anisotropy C_l^TT power spectrum
│   ├── section_14_matter_power_engine.py # 3D linear matter power spectrum P(k, z) engine
│   ├── section_15_bao_engine.py          # Baryon acoustic oscillation angular scale engine
│   ├── section_16_weak_lensing_engine.py # Metric slip lensing potential & S8 tension solver
│   ├── section_17_rsd_growth_engine.py   # Redshift-space distortion growth engine f*sigma8(z)
|   └── equations_results_VII.py          # # Volume II disk write module for equations_results_VI.txt
│
├── Test_files/                           # Automated physics test suite
│   ├── test_volume_1_physics.py          # Axiomatic, screening, and kinematic assertions
│   └── test_volume_2_physics.py          # Metric slip, growth rate, and S8 tension unit tests
│
└── assets_figures_vol1/                  # Rendered plot assets & 3D simulation snapshots
    ├── figure_6_1_vss_unification.png
    └── figure_7_1_3d_cosmological_simulation.png
