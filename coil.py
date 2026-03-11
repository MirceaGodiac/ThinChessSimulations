from dataclasses import dataclass
import numpy as np

@dataclass
class Coil:
    """
        Class representing a pcb coil.
        Attributes:
            coil_max_width_mm: The maximum width of the coil in millimeters.
            coil_max_length_mm: The maximum length of the coil in millimeters.
            trace_width_mm: The width of the coil traces in millimeters.
            trace_spacing_mm: The spacing between the coil traces in millimeters.
            num_layers: The number of layers in the coil.
            center_via_zone_width_mm: The width of the central via zone in millimeters.
            center_via_zone_length_mm: The length of the central via zone in millimeters.
            copper_weight_oz: The weight of the copper used for the coil in ounces per square foot.
    """
    coil_max_width_mm: float
    coil_max_length_mm: float
    trace_width_mm: float
    trace_spacing_mm: float
    num_layers: int
    center_via_zone_width_mm: float
    center_via_zone_length_mm: float
    copper_weight_oz: float
    
    def __post_init__(self):
        if self.trace_width_mm <= 0 or self.trace_spacing_mm < 0:
            raise ValueError("Trace width must be positive")
    
    @property
    def pitch(self) -> float:
        """
            The pitch of the coil, which is the distance from the center of one trace 
            to the center of the next trace.
        """
        return self.trace_width_mm + self.trace_spacing_mm

    @property
    def max_turns(self) -> int:
        """
            The maximum number of turns the coil can have.
            Formula: (min(coil_max_width_mm, coil_max_length_mm) - center_via_zone_width_mm) / (2 * pitch)
        """
        min_dimension_mm = min(self.coil_max_width_mm / 2, self.coil_max_length_mm / 2)
        return int((min_dimension_mm - self.center_via_zone_width_mm / 2) // self.pitch)
    
    def draw_points(self, max_shape_power: float = 10.0):
        """
            Draw the points of the coil using a superellipse formula to create a more compact shape.
             - max_shape_power: The maximum power to use for the superellipse shape. 
                                Higher values create a shape closer to a rectangle, 
                                while lower values create a shape closer to a circle.
        """
        n_pts = self.max_turns * 100  # Number of points to generate for the coil shape
        angles = np.linspace(0, self.max_turns * 2 * np.pi, n_pts)
        inner_radius = self.center_via_zone_width_mm / 2
        radii = inner_radius + (self.pitch / (2 * np.pi)) * angles
        shape_power = np.linspace(2.0, max_shape_power, n_pts)
        cos_a = np.cos(angles)
        sin_a = np.sin(angles)
        x_points = radii * np.sign(cos_a) * np.abs(cos_a) ** (2.0 / shape_power)
        y_points = radii * np.sign(sin_a) * np.abs(sin_a) ** (2.0 / shape_power)
        return x_points, y_points

    
    
    def calculate_trace_length_meters(self) -> float:
        """
            Calculate the total length of the coil traces in meters.
             - This is done by calculating the distance between consecutive points and summing them up,
                then multiplying by the number of layers and converting from millimeters to meters.
        """
        x_points, y_points = self.draw_points()
        dx = np.diff(x_points)
        dy = np.diff(y_points)
        return np.sum(np.sqrt(dx**2 + dy**2)) / 1000.0 * self.num_layers
    
    