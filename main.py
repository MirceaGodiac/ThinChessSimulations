from coil import Coil
from dataclasses import fields

if __name__ == "__main__":
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
    
    print("Coil Parameters:")
    print(f"Maximum number of turns: {coil.max_turns}")
    print(f"Estimated trace length: {coil.calculate_trace_length_meters():.2f} meters")