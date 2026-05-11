"""Froehlich (1995) embankment-dam breach parameter regressions.

The predecessor to :mod:`swmm_breach.froehlich` (Froehlich 2008).  The
1995 regressions were fit to a smaller breach database (63 cases) and
use different functional dependence on V_w and h_b; the 2008 update
revised both the fitted dataset (74 cases) and the exponents.

Including both regressions lets the package sample across *model
uncertainty* (which formulation is correct) in addition to the
within-model parameter uncertainty captured by :mod:`swmm_breach.uncertainty`.

All inputs and outputs are SI (metres, cubic metres, seconds).

Reference
---------
Froehlich, D. C. (1995). "Embankment Dam Breach Parameters Revisited."
Water Resources Engineering, Proc. 1995 ASCE Conf. on Water Resources
Engineering, San Antonio, TX, 887-891.
"""

from __future__ import annotations

from .breach import BreachGeometry, FailureMode


def average_breach_width(
    volume_m3: float, height_m: float, mode: FailureMode
) -> float:
    """Average breach bottom width B_avg [m].

    Froehlich (1995):  B_avg = 0.1803 * K_o * V_w^0.32 * h_b^0.19
        K_o = 1.4 (overtopping), 1.0 (piping)
    """
    k_o = 1.4 if mode is FailureMode.OVERTOPPING else 1.0
    return 0.1803 * k_o * volume_m3 ** 0.32 * height_m ** 0.19


def formation_time(volume_m3: float, height_m: float) -> float:
    """Breach formation time t_f [s].

    Froehlich (1995):  t_f [hr] = 0.00254 * V_w^0.53 * h_b^(-0.90)

    Returned in seconds for consistency with the rest of the package.
    """
    t_hr = 0.00254 * volume_m3 ** 0.53 * height_m ** -0.90
    return t_hr * 3600.0


def side_slope(mode: FailureMode) -> float:
    """Side slope (H per V); Froehlich (1995) recommends 0.9 across modes."""
    return 0.9


def predict(
    volume_m3: float,
    height_m: float,
    crest_elevation_m: float,
    mode: FailureMode,
) -> BreachGeometry:
    """Full :class:`BreachGeometry` from Froehlich (1995) regressions."""
    return BreachGeometry(
        bottom_width_m=average_breach_width(volume_m3, height_m, mode),
        height_m=height_m,
        side_slope_h_per_v=side_slope(mode),
        formation_time_s=formation_time(volume_m3, height_m),
        invert_elevation_m=crest_elevation_m - height_m,
    )
