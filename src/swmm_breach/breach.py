"""Core breach data structures used across the package."""

from dataclasses import dataclass
from enum import Enum


class FailureMode(Enum):
    """Embankment-dam breach failure mode."""

    OVERTOPPING = "overtopping"
    PIPING = "piping"


@dataclass(frozen=True)
class BreachGeometry:
    """Final geometry of a developed embankment-dam breach.

    All lengths in metres, time in seconds.

    Attributes
    ----------
    bottom_width_m
        Average bottom width of the trapezoidal breach (B_avg).
    height_m
        Vertical extent of the breach, crest down to invert.
    side_slope_h_per_v
        Side slope expressed as horizontal per vertical (H:V).
    formation_time_s
        Time from breach initiation to fully developed geometry (t_f).
    invert_elevation_m
        Final breach invert elevation (crest_elevation - height).
    """

    bottom_width_m: float
    height_m: float
    side_slope_h_per_v: float
    formation_time_s: float
    invert_elevation_m: float
