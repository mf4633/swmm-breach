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
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import froehlich, froehlich_1995
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


@dataclass(frozen=True)
class BreachModel:
    """A breach parameter regression with its log-residual uncertainty.

    Used by :func:`ensemble_simulate_multi_model` to draw realizations
    from a mixture of competing models, capturing both within-model
    parameter uncertainty (the ``sigma_log_*`` residuals) and the
    epistemic uncertainty about which model is correct (mixture weights).

    The two callables follow the signatures::

        b_avg_fn(volume_m3, height_m, mode) -> float  # metres
        t_f_fn(volume_m3, height_m, mode)   -> float  # seconds
    """

    name: str
    b_avg_fn: Callable[[float, float, FailureMode], float]
    t_f_fn: Callable[[float, float, FailureMode], float]
    side_slope_fn: Callable[[FailureMode], float]
    sigma_log_b_avg: float
    sigma_log_t_f: float
    weight: float = 1.0


def default_models() -> List[BreachModel]:
    """Default two-model ensemble: Froehlich (2008) and Froehlich (1995).

    The 1995 regressions were fit to a smaller dataset (63 cases) with
    different functional dependence on V_w and h_b; the 2008 update
    revised both the data and the exponents.  Sampling across both
    captures uncertainty about which generation of the regression is
    appropriate for a given dam.
    """
    return [
        BreachModel(
            name="froehlich_2008",
            b_avg_fn=froehlich.average_breach_width,
            t_f_fn=lambda v, h, m: froehlich.formation_time(v, h),
            side_slope_fn=froehlich.side_slope,
            sigma_log_b_avg=0.1097,
            sigma_log_t_f=0.1968,
            weight=1.0,
        ),
        BreachModel(
            name="froehlich_1995",
            b_avg_fn=froehlich_1995.average_breach_width,
            t_f_fn=lambda v, h, m: froehlich_1995.formation_time(v, h),
            side_slope_fn=froehlich_1995.side_slope,
            sigma_log_b_avg=0.137,
            sigma_log_t_f=0.220,
            weight=1.0,
        ),
    ]


@dataclass
class EnsembleHydrograph:
    """Monte Carlo ensemble of breach outflow hydrographs."""

    time_s: np.ndarray
    flows_m3s: np.ndarray  # shape (n_samples, n_steps)
    sampled_b_avg_m: np.ndarray
    sampled_t_f_s: np.ndarray
    sampled_model_index: Optional[np.ndarray] = None

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

    def plot_envelope(
        self,
        ax=None,
        low_pct: float = 5.0,
        high_pct: float = 95.0,
        show_realizations: bool = False,
        n_realizations: int = 20,
        rng: Optional[np.random.Generator] = None,
        envelope_color: str = "steelblue",
        median_color: str = "navy",
    ):
        """Plot the ensemble envelope: median line + low/high percentile band.

        Optionally overlay a random subset of individual realizations
        as thin lines.  Returns the matplotlib ``Axes``.

        Requires the optional ``viz`` extra: ``pip install swmm-breach[viz]``.
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

        t_min = self.time_s / 60.0
        low, med, high = self.envelope(low_pct=low_pct, high_pct=high_pct)

        ax.fill_between(
            t_min, low, high, alpha=0.25, color=envelope_color,
            label=f"{int(low_pct)}-{int(high_pct)}% envelope",
        )
        ax.plot(t_min, med, color=median_color, linewidth=2.0, label="median")

        if show_realizations:
            rng = rng if rng is not None else np.random.default_rng(0)
            n = min(n_realizations, self.n_samples)
            idx = rng.choice(self.n_samples, size=n, replace=False)
            for i in idx:
                ax.plot(t_min, self.flows_m3s[i], color="gray",
                        alpha=0.3, linewidth=0.5)

        ax.set_xlabel("Time (min)")
        ax.set_ylabel("Breach outflow (m$^3$/s)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper right")
        return ax


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


def ensemble_simulate_multi_model(
    storage: StorageCurve,
    crest_elevation_m: float,
    initial_stage_m: float,
    volume_m3: float,
    height_m: float,
    mode: FailureMode,
    n_samples: int,
    *,
    models: Optional[Sequence[BreachModel]] = None,
    inflow_m3s: float = 0.0,
    duration_s: Optional[float] = None,
    dt_s: float = 1.0,
    rng: Optional[np.random.Generator] = None,
) -> EnsembleHydrograph:
    """Multi-model Monte Carlo ensemble.

    Each realization (1) picks one of the supplied ``models`` according
    to its weight, (2) draws ``B_avg`` and ``t_f`` from that model's
    log-normal residual distribution, and (3) routes the resulting
    breach with :func:`swmm_breach.simulate`.

    Captures both *parametric* uncertainty (within-model residuals,
    after Wahl 2004) and *epistemic* uncertainty (which regression is
    appropriate, sampled across the model mixture).
    """
    if models is None:
        models = default_models()
    if len(models) == 0:
        raise ValueError("At least one model required")
    rng = rng if rng is not None else np.random.default_rng()

    weights = np.array([m.weight for m in models], dtype=float)
    if np.any(weights < 0):
        raise ValueError("Model weights must be non-negative")
    weights = weights / weights.sum()

    model_idx = rng.choice(len(models), size=n_samples, p=weights)
    b_samples = np.empty(n_samples)
    t_samples = np.empty(n_samples)
    side_samples = np.empty(n_samples)

    for i, mi in enumerate(model_idx):
        m = models[mi]
        b_central = m.b_avg_fn(volume_m3, height_m, mode)
        t_central = m.t_f_fn(volume_m3, height_m, mode)
        z_b = rng.normal(0.0, m.sigma_log_b_avg)
        z_t = rng.normal(0.0, m.sigma_log_t_f)
        b_samples[i] = b_central * 10.0 ** z_b
        t_samples[i] = t_central * 10.0 ** z_t
        side_samples[i] = m.side_slope_fn(mode)

    if duration_s is None:
        duration_s = max(float(t_samples.max()) * 4.0, 3600.0)

    n_steps = int(duration_s / dt_s) + 1
    flows = np.empty((n_samples, n_steps), dtype=float)

    invert = crest_elevation_m - height_m
    for i in range(n_samples):
        geom = BreachGeometry(
            bottom_width_m=float(b_samples[i]),
            height_m=height_m,
            side_slope_h_per_v=float(side_samples[i]),
            formation_time_s=float(t_samples[i]),
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
        sampled_b_avg_m=b_samples,
        sampled_t_f_s=t_samples,
        sampled_model_index=model_idx,
    )
