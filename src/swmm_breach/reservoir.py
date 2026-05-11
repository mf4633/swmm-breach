"""Reservoir storage curves and breach outflow hydraulics."""

from dataclasses import dataclass

import numpy as np

C_WEIR_BROAD_CRESTED = 1.7  # SI broad-crested weir coefficient


@dataclass
class StorageCurve:
    """Stage-storage relationship for a reservoir.

    ``stage_m`` and ``volume_m3`` are paired arrays sorted by stage
    ascending; both interpolations are linear and clamped at the ends.
    """

    stage_m: np.ndarray
    volume_m3: np.ndarray

    def __post_init__(self) -> None:
        self.stage_m = np.asarray(self.stage_m, dtype=float)
        self.volume_m3 = np.asarray(self.volume_m3, dtype=float)
        if self.stage_m.shape != self.volume_m3.shape:
            raise ValueError("stage_m and volume_m3 must have the same shape")
        if np.any(np.diff(self.stage_m) <= 0):
            raise ValueError("stage_m must be strictly increasing")

    def volume_at(self, stage: float) -> float:
        return float(np.interp(stage, self.stage_m, self.volume_m3))

    def stage_at(self, volume: float) -> float:
        return float(np.interp(volume, self.volume_m3, self.stage_m))


def trapezoidal_breach_outflow(
    head_m: float,
    bottom_width_m: float,
    side_slope_h_per_v: float,
    weir_coefficient: float = C_WEIR_BROAD_CRESTED,
) -> float:
    """Outflow through a developing trapezoidal breach [m^3/s].

    Treats the breach as a broad-crested weir with rectangular and
    triangular components:

        Q = C * B * h^1.5  +  (8/15) * C * (H:V) * h^2.5

    where ``head_m`` is the vertical distance from the upstream water
    surface down to the current breach invert.
    """
    if head_m <= 0.0 or bottom_width_m < 0.0:
        return 0.0
    rect = weir_coefficient * bottom_width_m * head_m ** 1.5
    tri = (8.0 / 15.0) * weir_coefficient * side_slope_h_per_v * head_m ** 2.5
    return rect + tri
