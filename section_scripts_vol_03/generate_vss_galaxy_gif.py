import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# =============================================================================
# 1. PHYSICAL CONSTANTS & VSS BASELINES (100% BARYONIC, ZERO DARK MATTER)
# =============================================================================
A_CRIT = 1.04217e-10       # Axiomatic acceleration gate scale a_crit [m/s^2]
G_CONST = 6.67430e-11      # Gravitational constant
M_SUN = 1.989e30           # Solar mass [kg]
KPC_TO_M = 3.0857e19       # Kiloparsec to meters

TOTAL_STARS = 6000         # High-density star particles for GIF rendering
M_DISK = 6.0e10 * M_SUN    # Total bare baryonic mass
R_DISK_SCALE = 3.5         # Exponential scale radius [kpc]

# VSS Constitutive Boost Function (NumPy Array-Safe)
def compute_vss_boost(gN):
    gN_safe = np.maximum(gN, 1e-20)
    Y = gN_safe / A_CRIT
    return 0.5 + 0.5 * np.sqrt(1.0 + 4.0 / Y)

def calculate_physics(r_kpc):
    r_m = np.maximum(0.05, r_kpc) * KPC_TO_M
    y = r_kpc / R_DISK_SCALE
    # Enclosed bare baryonic mass M_bar(r)
    m_enc = M_DISK * np.maximum(0.001, (1.0 - (1.0 + y) * np.exp(-y)))
    
    gN = (G_CONST * m_enc) / (r_m ** 2)   # Bare Newtonian field
    nu = compute_vss_boost(gN)            # VSS Strain boost
    geff = gN * nu                         # Effective acceleration
    v_m_s = np.sqrt(r_m * geff)           # Orbital velocity
    v_km_s = v_m_s / 1000.0
    phi = np.log(nu)                       # Scalar strain potential
    
    return gN, nu, geff, v_km_s, phi

# =============================================================================
# 2. LOGARITHMIC SPIRAL GALAXY GENERATION
# =============================================================================
np.random.seed(42) # Reproducible structure

r_kpc = np.zeros(TOTAL_STARS)
theta_0 = np.zeros(TOTAL_STARS)
z_kpc = np.zeros(TOTAL_STARS)
omega = np.zeros(TOTAL_STARS)

NUM_ARMS = 4
SPIRAL_WINDING = 2.0

for i in range(TOTAL_STARS):
    if np.random.rand() < 0.2:
        # Central Bulge (Exponential)
        r = -R_DISK_SCALE * 0.4 * np.log(1.0 - np.random.rand() * 0.999)
        th = np.random.rand() * 2 * np.pi
        z = np.random.normal(0, 0.4 * np.exp(-r / 1.5))
    else:
        # Logarithmic Spiral Arms
        r = 1.0 + (np.random.rand() ** 1.5) * 14.0
        arm_idx = i % NUM_ARMS
        arm_base_angle = arm_idx * (2 * np.pi / NUM_ARMS)
        spiral_angle = arm_base_angle + SPIRAL_WINDING * np.log(r)
        scatter = np.random.normal(0, 0.25 + r * 0.02)
        th = spiral_angle + scatter
        z = np.random.normal(0, 0.15 * np.exp(-r / 8.0))
        
    r_kpc[i] = r
    theta_0[i] = th
    z_kpc[i] = z
    
    # Calculate angular velocity omega for frame stepping
    _, _, _, v_km_s, _ = calculate_physics(r)
    omega[i] = ((v_km_s * 1000.0) / (r * KPC_TO_M)) * 2e14

# =============================================================================
# 3. MATPLOTLIB 3D ANIMATION & GIF RENDER
# =============================================================================
fig = plt.figure(figsize=(8, 8), dpi=120)
fig.patch.set_facecolor('#010206')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('#010206')

ax.axis('off')
ax.set_xlim(-16, 16)
ax.set_ylim(-16, 16)
ax.set_zlim(-8, 8)

# Color gradient based on radius
colors = plt.cm.cool(np.clip((r_kpc - 1.0) / 12.0, 0, 1))

# Initialize Star Scatter System
star_scatter = ax.scatter(
    r_kpc * np.cos(theta_0),
    r_kpc * np.sin(theta_0),
    z_kpc,
    c=colors,
    s=1.2,
    alpha=0.85,
    depthshade=True
)

# Initialize Deformable 3D Strain Grid Beneath Galaxy
grid_x, grid_y = np.meshgrid(np.linspace(-15, 15, 25), np.linspace(-15, 15, 25))
grid_r = np.sqrt(grid_x**2 + grid_y**2)
_, _, _, _, grid_phi = calculate_physics(grid_r)
grid_z = -2.5 - grid_phi * 1.2

grid_wire = ax.plot_wireframe(grid_x, grid_y, grid_z, color='#0284c7', alpha=0.25, linewidth=0.5)

# Add Title Annotation
title_text = ax.text2D(
    0.05, 0.93,
    "VSS 4D COSMOLOGY ENGINE\nPure Baryonic Spiral Galaxy (Ωc ≡ 0.000)",
    color='#38bdf8', fontsize=11, fontweight='bold', transform=ax.transAxes
)

# Frame Animation Function
num_frames = 60
dt = 0.05

def update(frame):
    # Rotate camera slightly for 3D parallax effect
    ax.view_init(elev=35 + 5 * np.sin(frame * 0.05), azim=frame * 0.8)
    
    # Update star orbital positions according to VSS Vflat velocity
    current_theta = theta_0 + omega * frame * dt
    x = r_kpc * np.cos(current_theta)
    y = r_kpc * np.sin(current_theta)
    
    star_scatter._offsets3d = (x, y, z_kpc)
    return star_scatter,

print("[*] Generating VSS Galaxy GIF animation (60 frames)... Please wait.")
anim = FuncAnimation(fig, update, frames=num_frames, interval=50, blit=False)

# Export directly to .gif file
gif_filename = 'vss_galaxy_simulation.gif'
writer = PillowWriter(fps=20)
anim.save(gif_filename, writer=writer)

plt.close()
print(f"[✓] SUCCESS: Animated GIF saved as '{gif_filename}' in your current working directory.")