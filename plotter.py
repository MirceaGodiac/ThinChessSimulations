"""Plots the results of the experiments."""

from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
from coil import Coil

@dataclass
class Plotter:
    coil: Coil

    def plot_coil(self):
        x, y = self.coil.draw_points()

        fig, ax = plt.subplots(figsize=(8, 8), facecolor='#121212')
        ax.set_facecolor('#121212')
        ax.set_aspect('equal')

        # set the axis limits before calculating the scale,
        # otherwise matplotlib defaults to a 0-1 grid and the math explodes
        margin = self.coil.pitch * 2
        ax.set_xlim(min(x) - margin, max(x) + margin)
        ax.set_ylim(min(y) - margin, max(y) + margin)

        # Force a draw so the renderer actually builds the bounding boxes
        fig.canvas.draw()

        # Extract the physical screen width of the axis in inches
        bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        data_width = ax.get_xlim()[1] - ax.get_xlim()[0]

        # Calculate exactly how many points represent 1 mm in your specific window
        points_per_mm = (bbox.width * 72) / data_width

        # Scale your physical copper width to matplotlib points
        real_linewidth = self.coil.trace_width_mm * points_per_mm

        # Draw the trace using the dynamically calculated point width
        # solid_capstyle='butt' prevents the corners from rounding over into your spacing gap
        ax.plot(x, y, color='#ff7f0e', linewidth=real_linewidth, solid_capstyle='butt')

        plt.title('Squircle Planar Coil Geometry (0.4mm Scaled Copper)', color='white')
        plt.xlabel('X (mm)', color='gray')
        plt.ylabel('Y (mm)', color='gray')
        plt.grid(True, color='gray', linestyle='--', alpha=0.3)
        plt.tick_params(colors='white')

        plt.show()

    def plot_pwm_current(self, resistance_ohms, inductance_henries, voltage=12.0, freq_hz=30000, duty_cycle=0.8):
        # Time constants
        period = 1.0 / freq_hz
        t_on = period * duty_cycle
        t_off = period * (1 - duty_cycle)

        # Simulation parameters
        num_cycles = 5
        points_per_cycle = 1000
        t_total = np.linspace(0, num_cycles * period, num_cycles * points_per_cycle)
        current_vals = np.zeros_like(t_total)

        # Initial states
        i_current = 0.0
        tau = inductance_henries / resistance_ohms
        i_max_steady = voltage / resistance_ohms

        dt = t_total[1] - t_total[0]

        # Step through time
        for idx in range(1, len(t_total)):
            t_in_cycle = t_total[idx] % period

            if t_in_cycle < t_on:
                # Charging: current moves toward V/R
                # dI/dt = (V - I*R) / L
                di = ((voltage - i_current * resistance_ohms) / inductance_henries) * dt
            else:
                # Discharging: current moves toward 0 (assuming a flyback diode)
                # dI/dt = (-I*R) / L
                di = ((-i_current * resistance_ohms) / inductance_henries) * dt

            i_current += di
            current_vals[idx] = i_current

        # Plotting
        plt.figure(figsize=(10, 5), facecolor='#121212')
        ax = plt.gca()
        ax.set_facecolor('#121212')

        plt.plot(t_total * 1e6, current_vals, color='#00ff00', linewidth=2, label="Actual Current")
        plt.axhline(y=i_max_steady, color='red', linestyle='--', alpha=0.5, label="Theoretical Max (DC)")

        plt.title(f"PWM Current Response @ {freq_hz / 1000}kHz", color='white')
        plt.xlabel("Time (microseconds)", color='gray')
        plt.ylabel("Current (Amps)", color='gray')
        plt.legend()
        plt.grid(True, color='gray', linestyle='--', alpha=0.3)
        plt.tick_params(colors='white')
        plt.show()

    def calculate_steady_state_temp_c(self, current_amps: float, ambient_temp_c: float = 25.0) -> float:
        """
        Calculates the estimated max temperature using IPC-2152 for internal layers.
        Formula: delta_T = (I / (k * A^m)) ^ (1/n)
        """
        # Cross-sectional area in square mils (1 m^2 = 1.55e9 sq mils)
        thickness_m = (self.coil.copper_weight_oz * 35.56) / 1e6
        width_m = self.coil.trace_width_mm / 1000.0
        area_sq_mils = (thickness_m * width_m) * 1.55e9

        # IPC-2152 constants for internal traces (worst-case cooling)
        k = 0.024
        m = 0.725
        n = 0.44

        # Calculate temperature rise
        delta_t = (current_amps / (k * (area_sq_mils ** m))) ** (1.0 / n)

        return ambient_temp_c + delta_t

    def plot_thermals_vs_current(self, max_amps: float = 3.0, ambient_temp_c: float = 25.0):
        """
        Plots the expected coil temperature against current.
        """
        currents = np.linspace(0.1, max_amps, 50)
        temps = [self.calculate_steady_state_temp_c(i, ambient_temp_c) for i in currents]

        plt.figure(figsize=(8, 5))
        plt.plot(currents, temps, color='red', linewidth=2)
        plt.axvline(1.4, color='blue', linestyle='--', label='Your 1.4A Target')

        # Mark the glass transition temp of standard FR4 as a warning line
        plt.axhline(130, color='black', linestyle=':', label='FR4 Tg (~130°C)')

        plt.title("Steady-State Coil Temperature vs. Current")
        plt.xlabel("Current (Amps)")
        plt.ylabel("Maximum Temperature (°C)")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.show()