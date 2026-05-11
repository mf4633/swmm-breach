"""Monte Carlo uncertainty propagation for Froehlich (2008) breach
parameters, after Wahl (2004).

Wahl [#wahl2004]_ demonstrated that empirical embankment-dam breach
parameter regressions carry standard errors of estimate (in log10
units) on the order of 0.1 to 1.0, implying factor-of-2 to factor-of-10
uncertainty on predicted peak flows.  Yet engineering practice
overwhelmingly reports a single deterministic peak.  This module
implements the Monte Carlo response Wahl recommended: sample the
predicted breach parameters within their published log-normal residual
distributions, route the breach for each realization, and report the
resulting ensemble of hydrographs with percentile envelopes.

The default sigma values come from Froehlich (2008)'s Table 11 of
fitted-vs-observed residuals; users with project-specific calibration
data can override them.

References
----------
.. [#wahl2004] Wahl, T. L. (2004). "Uncertainty of Predictions of
   Embankment Dam Breach Parameters." J. Hydraul. Eng., 130(5), 389-397.
.. [#froehlich2008] Froehlich, D. C. (2008). "Embankment Dam Breach
   Parameters and Their Uncertainties." J. Hydraul. Eng., 134(12),
   1708-1721.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import numpy as np

from . import froehlich
from .breach import BreachGeometry, FailureMode
from .hydrograph import simulate
from .reservoir import StorageCurve


@dataclass(frozen=True)
class FroehlichUncertainty:
    """Standard errors of estimate (in log10 units) for Froehlich (2008).

    Defaults are consistent with the residual statistics reported in
    Froehlich (2008) for the average bottom width and formation-time
    regressions.  Override for project-specific calibration.
    """

    sigma_log_b_avg: float = 0.1097
    sigma_log_t_f: float = 0.1968


@dataclass
class EnsembleHydrograph:
    """Monte Carlo ensemble of breach outflow hydrographs."""

    time_s: np.ndarray
    flows_m3s: np.ndarray  # shape (n_samples, n_steps)
    sampled_b_avg_m: np.ndarray
    sampled_t_f_s: np.ndarray

    @property
    def n_samples(self) -> int:
        return self.flows_m3s.shape[0]

    def percentile(self, p: float) -> np.ndarray:
        """Per-time-step percentile across the ensemble."""
        return np.percentile(self.flows_m3s, p, axis=0)

    def envelope(
        self, low_pct: float = 5.0, high_pct: float = 95.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return ``(low, median, high)`` per-time-step envelope arrays."""
        return (
            self.percentile(low_pct),
            self.percentile(50.0),
            self.percentile(high_pct),
        )

    @property
    def peak_flows_m3s(self) -> np.ndarray:
        """Peak flow per realization, length ``n_samples``."""
        return self.flows_m3s.max(axis=1)

    def peak_percentile(self, p: float) -> float:
        """Percentile of the per-realization peak distribution."""
        return float(np.percentile(self.peak_flows_m3s, p))


def sample_breach_parameters(
    volume_m3: float,
    height_m: float,
    mode: FailureMode,
    n_samples: int,
    *,
    uncertainty: FroehlichUncertainty = FroehlichUncertainty(),
    rng: Optional[np.random.Generator] = None,
) -> Dict[str, np.ndarray]:
    """Draw ``n_samples`` log-normal MC realizations of B_avg and t_f.

    Wahl (2004) showed that breach-parameter regression residuals are
    well approximated by a log-normal distribution centered on the
    predicted value.  Samples are::

        B_i = B_central * 10 ** Z_i,        Z_i ~ Normal(0, sigma_log_B)
        t_i = t_central * 10 ** W_i,        W_i ~ Normal(0, sigma_log_t)

    Returns
    -------
    dict with arrays of shape ``(n_samples,)`` keyed
    ``"bottom_width_m"``, ``"formation_time_s"``,
    ``"side_slope_h_per_v"``.
    """
    if n_samples < 1:
        raise ValueError("n_samples must be >= 1")
    rng = rng if rng is not None else np.random.default_rng()

    b_central = froehlich.average_breach_width(volume_m3, height_m, mode)
    t_central = froehlich.formation_time(volume_m3, height_m)

    z_b = rng.normal(0.0, uncertainty.sigma_log_b_avg, n_samples)
    z_t = rng.normal(0.0, uncertainty.sigma_log_t_f, n_samples)

    return {
        "bottom_width_m": b_central * 10.0 ** z_b,
        "formation_time_s": t_central * 10.0 ** z_t,
        "side_slope_h_per_v": np.full(n_samples, froehlich.side_slope(mode)),
    }


def ensemble_simulate(
    storage: StorageCurve,
    crest_elevation_m: float,
    initial_stage_m: float,
    volume_m3: float,
    height_m: float,
    mode: FailureMode,
    n_samples: int,
    *,
    uncertainty: FroehlichUncertainty = FroehlichUncertainty(),
    inflow_m3s: float = 0.0,
    duration_s: Optional[float] = None,
    dt_s: float = 1.0,
    rng: Optional[np.random.Generator] = None,
) -> EnsembleHydrograph:
    """Run a Monte Carlo ensemble of breach simulations.

    Each realization independently samples ``B_avg`` and ``t_f`` from
    the Froehlich (2008) point estimate using the supplied log-normal
    residual sigmas (defaults from :class:`FroehlichUncertainty`),
    constructs the corresponding :class:`BreachGeometry`, and routes
    the breach with :func:`swmm_breach.simulate`.

    All realizations are routed on a common time grid so that
    percentile envelopes can be computed pointwise in time.
    """
    samples = sample_breach_parameters(
        volume_m3, height_m, mode, n_samples,
        uncertainty=uncertainty, rng=rng,
    )

    if duration_s is None:
        duration_s = max(float(samples["formation_time_s"].max()) * 4.0, 3600.0)

    n_steps = int(duration_s / dt_s) + 1
    flows = np.empty((n_samples, n_steps), dtype=float)

    invert = crest_elevation_m - height_m
    for i in range(n_samples):
        geom = BreachGeometry(
            bottom_width_m=float(samples["bottom_width_m"][i]),
            height_m=height_m,
            side_slope_h_per_v=float(samples["side_slope_h_per_v"][i]),
            formation_time_s=float(samples["formation_time_s"][i]),
            invert_elevation_m=invert,
        )
        hg = simulate(
            geometry=geom,
            storage=storage,
            crest_elevation_m=crest_elevation_m,
            initial_stage_m=initial_stage_m,
            inflow_m3s=inflow_m3s,
            duration_s=duration_s,
            dt_s=dt_s,
        )
        flows[i, : len(hg.outflow_m3s)] = hg.outflow_m3s

    return EnsembleHydrograph(
        time_s=np.arange(n_steps) * dt_s,
        flows_m3s=flows,
        sampled_b_avg_m=samples["bottom_width_m"],
        sampled_t_f_s=samples["formation_time_s"],
    )
