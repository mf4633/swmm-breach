"""Froehlich (2008) embankment-dam breach parameter regressions.

All inputs and outputs are SI (metres, cubic metres, seconds).

Reference
---------
Froehlich, D. C. (2008). "Embankment Dam Breach Parameters and Their
Uncertainties." Journal of Hydraulic Engineering, 134(12), 1708-1721.
"""

import math

from .breach import BreachGeometry, FailureMode

G = 9.80665  # gravitational acceleration, m/s^2


def average_breach_width(
    volume_m3: float, height_m: float, mode: FailureMode
) -> float:
    """Average breach bottom width B_avg [m].

    B_avg = 0.27 * K_o * V_w^0.32 * h_b^0.04
        K_o = 1.3 (overtopping), 1.0 (piping)
    """
    k_o = 1.3 if mode is FailureMode.OVERTOPPING else 1.0
    return 0.27 * k_o * volume_m3 ** 0.32 * height_m ** 0.04


def formation_time(volume_m3: float, height_m: float) -> float:
    """Breach formation time t_f [s].

    t_f = 63.2 * sqrt(V_w / (g * h_b^2))
    """
    return 63.2 * math.sqrt(volume_m3 / (G * height_m ** 2))


def side_slope(mode: FailureMode) -> float:
    """Recommended side slope (H per V), Froehlich (2008)."""
    return 1.0 if mode is FailureMode.OVERTOPPING else 0.7


def predict(
    volume_m3: float,
    height_m: float,
    crest_elevation_m: float,
    mode: FailureMode,
) -> BreachGeometry:
    """Full BreachGeometry from Froehlich (2008) regressions."""
    return BreachGeometry(
        bottom_width_m=average_breach_width(volume_m3, height_m, mode),
        height_m=height_m,
        side_slope_h_per_v=side_slope(mode),
        formation_time_s=formation_time(volume_m3, height_m),
        invert_elevation_m=crest_elevation_m - height_m,
    )
