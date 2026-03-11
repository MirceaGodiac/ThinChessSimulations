"""
Main execution script for the 2mm Chess Board Electromagnetic Simulator.
"""

from coil import Coil
from physics import Physics
from plotter import Plotter

def main():
    print("--- 2mm Solid-State Chess Board Simulator ---")
    
    # hardware constraints
    coil = Coil(
        coil_max_width_mm=16.6,
        coil_max_length_mm=16.6,
        trace_width_mm=0.13,
        trace_spacing_mm=0.1,
        num_layers=1,
        center_via_zone_width_mm=2.0,
        center_via_zone_length_mm=2.0,
        copper_weight_oz=1.0
    )

    # Initialize Physics Class and calculate parameters
    physics = Physics(coil=coil)
    resistance = physics.calculate_resistance_ohms()
    inductance = physics.calculate_inductance_henries()

    print(f"[*] Geometry: {coil.max_turns} turns, {coil.calculate_trace_length_meters():.3f} meters of trace")
    print(f"[*] Electrical: R = {resistance:.3f} Ω, L = {inductance * 1e6:.3f} µH")
    print("\n[*] Launching diagnostic plots. Close each window to load the next...")

    plotter = Plotter(coil=coil)
    
    # Plot physical PCB geometry
    plotter.plot_coil()
    
    # 30kHz PWM Response
    plotter.plot_pwm_current(
        resistance_ohms=resistance, 
        inductance_henries=inductance, 
        voltage=12.0, 
        freq_hz=30000, 
        duty_cycle=0.8
    )
    
    # IPC-2152 Thermal Limits
    plotter.plot_thermals_vs_current(max_amps=3.0)
    print("[*] Simulation complete.")

if __name__ == "__main__":
    main()