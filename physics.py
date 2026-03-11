"""Calculate physics for the coil, resistance, inductance, etc."""

from coil import Coil
from dataclasses import dataclass
import numpy as np

@dataclass
class Physics:
    coil: Coil
    copper_resistivity_ohm_m: float = 1.68e-8  # Ohm-meter for copper

    def calculate_resistance_ohms(self) -> float:
        """
                Calculate the resistance of the coil in ohms.
                    R = rho * (L / A)
                    where:
                        R = resistance (ohms)
                        rho = resistivity of the material (ohm-meters)
                        L = length of the conductor (meters)
                        A = cross-sectional area of the conductor (square meters)
        :return resistance of coil in ohms
        """
        trace_length_m = self.coil.calculate_trace_length_meters()

        # thickness in meters: (oz * 35.56) / 1,000,000
        thickness_m = (self.coil.copper_weight_oz * 35.56) / 1e6

        # width in meters: mm / 1,000
        width_m = self.coil.trace_width_mm / 1000.0

        area_m2 = thickness_m * width_m

        # R = rho * (L / A)
        r_single_layer = self.copper_resistivity_ohm_m * (trace_length_m / area_m2)

        # Series total for all layers
        return r_single_layer

    def calculate_inductance_henries(self) -> float:
        """
        Modified Wheeler Formula for square/squircle planar spirals.
        K1 = 2.34, K2 = 2.75 for square layouts.
        Formula: L = (K1 * mu_0 * N^2 * d_avg) / (1 + K2 * fill_factor)
        where:
            L = inductance in henries
            mu_0 = permeability of free space (4 * pi * 1e-7 H/m)
            N = total number of turns (across all layers)
            d_avg = average diameter of the coil (meters)
            fill_factor = (d_out - d_in) / (d_out + d_in)
        """
        mu_0 = 4 * np.pi * 1e-7

        # N is total turns across ALL layers (N_layer * num_layers)
        n_total = self.coil.max_turns * self.coil.num_layers

        d_out = self.coil.coil_max_width_mm / 1000.0
        # d_in is the hole in the middle
        d_in = self.coil.center_via_zone_width_mm / 1000.0

        d_avg = (d_out + d_in) / 2.0
        fill_factor = (d_out - d_in) / (d_out + d_in)

        k1, k2 = 2.34, 2.75  # Square/Squircle constants

        l_henries = (k1 * mu_0 * (n_total ** 2) * d_avg) / (1 + k2 * fill_factor)
        return l_henries

    def simulate_biot_savart(self) -> float:
        """
            Compute the max magnetic field using the formula:
            B = (mu_0 * N * I) / 2 * R
            Where:
                B - Magnetic field intensity
                mu_0 - Permeability of free space
                N - number of turns
                I - current intensity
                R - Radius of coil
        """

        mu_0 = 4 * np.pi * 1e-7

        n_turns = self.coil.max_turns * self.coil.num_layers
        current_intensity = 1.4 #Amperes
        area = self.coil.coil_max_length_mm * self.coil.coil_max_width_mm

        magFieldIntensity = (mu_0 * n_turns * current_intensity) / area

        return magFieldIntensity






