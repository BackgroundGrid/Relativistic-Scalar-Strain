import numpy as np

# Physical and Cosmological Constants
C = 299792458.0          # Speed of light in vacuum (m/s)
G = 6.67430e-11          # Gravitational constant (m^3 kg^-1 s^-2)
H0 = 70.0                # Hubble constant (km/s/Mpc)

# RSS / VSS Specific Parameters
A_CRIT = 1.08e-10        # Critical vacuum strain acceleration scale (m/s^2)
OMEGA_VAC = 1.0 - (1.0 / np.pi)  # Asymptotic vacuum stress fraction (~ 0.68169)
