import pytest
from coil import Coil

def test_coil_max_turns():
    # Test with known dimensions
    coil = Coil(16.6, 16.6, 0.13, 0.1, 1, 2.0, 2.0, 1.0)
    # (16.6/2 - 2.0/2) / (0.13 + 0.1) = (8.3 - 1.0) / 0.23 = 31.73 -> 31 turns
    assert coil.max_turns == 31
        
def test_invalid_dimensions_fail():
    """
    Ensure the Coil class rejects invalid physical parameters 
    during initialization.
    """
    with pytest.raises(ValueError, match="Trace width must be positive"):
        Coil(
            coil_max_width_mm=10, 
            coil_max_length_mm=10, 
            trace_width_mm=0,  # Invalid: triggers ValueError
            trace_spacing_mm=0, 
            num_layers=1, 
            center_via_zone_width_mm=2.0, 
            center_via_zone_length_mm=2.0, 
            copper_weight_oz=1.0
        )