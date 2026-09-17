import os
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Directory Pathing
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets_figures_vol1")
os.makedirs(ASSETS_DIR, exist_ok=True)

def run_3d_photorealistic_cosmos():
    print("======================================================================")
    print("SECTION 7: PHOTOREALISTIC 3D COSMOS & VACUUM STRAIN SIMULATION")
    print("======================================================================")
    
    # -------------------------------------------------------------------------
    # Physical Constants & RSS/VSS Geometric Parameters
    # -------------------------------------------------------------------------
    c = 2.99792458e8                     # m/s
    H0_SI = 2.18428524e-18               # s^-1 (67.4 km/s/Mpc)
    a_crit = (c * H0_SI) / (2.0 * np.pi) # ~ 1.0422e-10 m/s^2
    Omega_vac = 1.0 - (1.0 / np.pi)       # ~ 0.6817 (Vacuum Stress Saturation)

    # -------------------------------------------------------------------------
    # Canvas & 3D Deep Space Setup
    # -------------------------------------------------------------------------
    fig = plt.figure(figsize=(14, 9), facecolor='#020205')
    ax = fig.add_subplot(111, projection='3d', facecolor='#020205')
    
    # Enable deep space dark theme
    ax.set_xlim([-120, 120])
    ax.set_ylim([-120, 120])
    ax.set_zlim([-120, 120])
    ax.axis('off')  # Seamless infinite cosmos view

    # -------------------------------------------------------------------------
    # 1. Deep Field Background Skybox Stars (Spectral Types O, B, A, F, G, K, M)
    # -------------------------------------------------------------------------
    np.random.seed(1337)
    num_sky_stars = 2200
    
    # Random spherical distribution at outer edge
    r_sky = np.random.uniform(150, 220, num_sky_stars)
    theta_sky = np.random.uniform(0, 2*np.pi, num_sky_stars)
    phi_sky = np.random.uniform(-np.pi/2, np.pi/2, num_sky_stars)
    
    x_sky = r_sky * np.cos(phi_sky) * np.cos(theta_sky)
    y_sky = r_sky * np.cos(phi_sky) * np.sin(theta_sky)
    z_sky = r_sky * np.sin(phi_sky)
    
    # Astronomical spectral classification colors
    spectral_colors = ['#9bb0ff', '#aabfff', '#cad8ff', '#f8f7ff', '#fff4ea', '#ffd2a1', '#ff8a65']
    sky_colors = np.random.choice(spectral_colors, size=num_sky_stars, p=[0.05, 0.10, 0.15, 0.20, 0.25, 0.15, 0.10])
    sky_sizes = np.random.exponential(scale=1.2, size=num_sky_stars) + 0.2
    
    ax.scatter(x_sky, y_sky, z_sky, c=sky_colors, s=sky_sizes, alpha=0.75, depthshade=True)

    # -------------------------------------------------------------------------
    # 2. Photorealistic Spiral Galaxy (Logarithmic Arms & Stellar Bulge)
    # -------------------------------------------------------------------------
    num_galaxy_stars = 3500
    
    # Core Bulge Stars (Dense yellow/white core)
    r_core = np.random.exponential(scale=4.5, size=800)
    theta_core = np.random.uniform(0, 2*np.pi, 800)
    phi_core = np.random.uniform(-np.pi/2, np.pi/2, 800)
    
    x_core = r_core * np.cos(phi_core) * np.cos(theta_core)
    y_core = r_core * np.cos(phi_core) * np.sin(theta_core)
    z_core = r_core * np.sin(phi_core) * 0.5
    core_colors = ['#fff8e7'] * 800
    
    # Logarithmic Spiral Arms (2 major arms + dust dispersion)
    arms_count = 2
    stars_per_arm = (num_galaxy_stars - 800) // arms_count
    arm_x, arm_y, arm_z, arm_colors_list, arm_radii, arm_angles = [], [], [], [], [], []
    
    for arm in range(arms_count):
        arm_phase = arm * np.pi
        r_val = np.random.uniform(5, 55, stars_per_arm)
        # Logarithmic spiral equation: theta = (1/b) * ln(r/a) + arm_phase
        theta_val = 2.2 * np.log(r_val / 3.0) + arm_phase + np.random.normal(0, 0.28, stars_per_arm)
        
        # Disk thickness & dispersion
        z_val = np.random.normal(0, 1.2 * np.exp(-r_val / 35.0), stars_per_arm)
        
        # Color gradient: Young blue stars in outer arms, warm yellow in inner arms
        arm_colors = []
        for r in r_val:
            if r < 18:
                arm_colors.append('#ffe4b5')  # Warm yellow-white
            elif r < 35:
                arm_colors.append('#ffffff')  # Crisp white
            else:
                arm_colors.append('#80d8ff')  # Deep hot starburst blue
                
        arm_x.extend(r_val * np.cos(theta_val))
        arm_y.extend(r_val * np.sin(theta_val))
        arm_z.extend(z_val)
        arm_colors_list.extend(arm_colors)
        arm_radii.extend(r_val)
        arm_angles.extend(theta_val)
        
    # Combine Core and Arms
    all_star_x = np.concatenate([x_core, arm_x])
    all_star_y = np.concatenate([y_core, arm_y])
    all_star_z = np.concatenate([z_core, arm_z])
    all_star_colors = core_colors + arm_colors_list
    all_star_radii = np.concatenate([r_core, arm_radii])
    all_star_angles = np.concatenate([theta_core, arm_angles])

    # Dynamic Scatter Object for Galaxy
    galaxy_scat = ax.scatter(all_star_x, all_star_y, all_star_z, c=all_star_colors, s=2.2, alpha=0.85)

    # -------------------------------------------------------------------------
    # 3. Volumetric Cluster Nebulae & Light Deflection Geodesics
    # -------------------------------------------------------------------------
    # Gas Halos around Deep Space Clusters
    cluster_centers = np.array([[-60, 45, 30], [55, -60, -25]])
    for cx, cy, cz in cluster_centers:
        ax.scatter([cx], [cy], [cz], c='#e040fb', s=1200, alpha=0.12, edgecolors='none')
        ax.scatter([cx], [cy], [cz], c='#00e5ff', s=450, alpha=0.25, edgecolors='none')

    # Photonic Metric Geodesic Deflection Ray
    lensing_ray, = ax.plot([], [], [], color='#ffe082', linestyle='-', lw=1.8, alpha=0.9, 
                           label='Conformal Photon Deflection Vector')

    # -------------------------------------------------------------------------
    # 4. Corrected HUD Telemetry Box (Zero Dark Energy)
    # -------------------------------------------------------------------------
    hud_text = fig.text(
        0.03, 0.86, "", color='#00f5d4', fontsize=10, family='monospace',
        bbox=dict(boxstyle='round,pad=0.7', facecolor='#050814', edgecolor='#00f5d4', alpha=0.85)
    )

    def animate(frame):
        # Camera Pan in Deep Space
        elev = 26 + 6 * np.sin(frame * 0.012)
        azim = (frame * 0.35) % 360
        ax.view_init(elev=elev, azim=azim)
        
        # Scale-Invariant Rotation Velocity ($V_{RSSV}$) Dynamics
        v_flat = 160.0  # km/s scaling factor
        delta_theta = (v_flat / (all_star_radii + 3.0)) * 0.02
        new_angles = all_star_angles + delta_theta * frame
        
        new_x = all_star_radii * np.cos(new_angles)
        new_y = all_star_radii * np.sin(new_angles)
        galaxy_scat._offsets3d = (new_x, new_y, all_star_z)
        
        # Light Deflection Beam passing through the Vacuum Strain Tensor
        t_lens = np.linspace(-110, 110, 80)
        lens_bend = 15.0 * np.exp(-(t_lens / 32.0)**2) * np.cos(frame * 0.05)
        lensing_ray.set_data(t_lens, lens_bend - 20.0)
        lensing_ray.set_3d_properties(t_lens * 0.12)

        # Telemetry HUD Display
        hud_text.set_text(
            f"=================== RSS/VSS COSMIC SIMULATOR ===================\n"
            f" Critical Acceleration Threshold (a_crit) : {a_crit:.4e} m/s²\n"
            f" Vacuum Stress Saturation Density (Omega_vac): {Omega_vac:.4f}  [1 - 1/π]\n"
            f" Dark Energy & Dark Matter Fluids         : EXPLICITLY ELIMINATED (0.00%)\n"
            f" Hubble Expansion Parameter (H0)           : 67.4 km/s/Mpc\n"
            f" Camera Orbital Viewstep                   : Epoch {frame:04d} | Azimuth {azim:.1f}°"
        )
        
        return galaxy_scat, lensing_ray, hud_text

    print("Rendering Photorealistic Cosmos Window...")
    anim = FuncAnimation(fig, animate, frames=360, interval=30, blit=False)
    
    # Save High-Res Snapshot for Volume 1 Figures
    output_fig = os.path.join(ASSETS_DIR, "figure_7_1_3d_cosmological_simulation.png")
    plt.savefig(output_fig, dpi=300, facecolor='#020205', bbox_inches='tight')
    print(f"[SUCCESS] Photorealistic snapshot saved to asset registry:\n  -> {output_fig}")
    
    try:
        plt.show()
    except Exception as e:
        print(f"Notice: Live window GUI output completed ({e}).")

if __name__ == "__main__":
    run_3d_photorealistic_cosmos()