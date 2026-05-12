"""Breach outflow hydrograph generation by level-pool reservoir routing."""

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .breach import BreachGeometry
from .reservoir import StorageCurve, trapezoidal_breach_outflow


@dataclass
class Hydrograph:
    """Breach outflow time series with the reservoir state behind it."""

    time_s: np.ndarray
    outflow_m3s: np.ndarray
    stage_m: np.ndarray
    breach_bottom_width_m: np.ndarray
    breach_invert_m: np.ndarray

    @property
    def peak_outflow_m3s(self) -> float:
        return float(np.max(self.outflow_m3s))

    @property
    def time_to_peak_s(self) -> float:
        return float(self.time_s[int(np.argmax(self.outflow_m3s))])

    def plot(self, ax=None, **kwargs):
        """Plot the breach outflow hydrograph.

        Returns the matplotlib ``Axes`` so the caller can add
        annotations, legends, or save the figure.  Requires the
        optional ``viz`` extra: ``pip install swmm-breach[viz]``.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError as e:
            raise ImportError(
                "matplotlib is required for plotting; "
                "install with `pip install swmm-breach[viz]`"
            ) from e
        if ax is None:
            _, ax = plt.subplots(figsize=(8, 4))
        ax.plot(self.time_s / 60.0, self.outflow_m3s, **kwargs)
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Breach outflow (m$^3$/s)")
        ax.grid(True, alpha=0.3)
        return ax


def simulate(
    geometry: BreachGeometry,
    storage: StorageCurve,
    crest_elevation_m: float,
    initial_stage_m: float,
    inflow_m3s: float = 0.0,
    duration_s: Optional[float] = None,
    dt_s: float = 1.0,
) -> Hydrograph:
    """Linear-growth breach + level-pool routing.

    The breach bottom width grows linearly from 0 to
    ``geometry.bottom_width_m`` over ``geometry.formation_time_s``;
    the invert simultaneously drops from ``crest_elevation_m`` to
    ``geometry.invert_elevation_m``.

    Mass balance:  dV/dt = inflow - outflow
    Outflow:       broad-crested weir on the developing trapezoid.
    """
    if duration_s is None:
        duration_s = max(geometry.formation_time_s * 4.0, 3600.0)

    n_steps = int(duration_s / dt_s) + 1
    t = np.arange(n_steps) * dt_s
    Q = np.zeros(n_steps)
    H = np.zeros(n_steps)
    B = np.zeros(n_steps)
    INV = np.zeros(n_steps)

    H[0] = initial_stage_m
    volume = storage.volume_at(initial_stage_m)

    for i in range(n_steps):
        progress = min(t[i] / geometry.formation_time_s, 1.0)
        bw = progress * geometry.bottom_width_m
        invert = crest_elevation_m - progress * geometry.height_m
        head = max(H[i] - invert, 0.0)
        q_out = trapezoidal_breach_outflow(
            head, bw, geometry.side_slope_h_per_v
        )

        Q[i] = q_out
        B[i] = bw
        INV[i] = invert

        if i + 1 < n_steps:
            volume = max(volume + (inflow_m3s - q_out) * dt_s, 0.0)
            H[i + 1] = storage.stage_at(volume)

    return Hydrograph(
        time_s=t,
        outflow_m3s=Q,
        stage_m=H,
        breach_bottom_width_m=B,
        breach_invert_m=INV,
    )
