"""Smoke tests for the matplotlib plotting helpers (optional viz extra)."""

import numpy as np
import pytest

# Skip the entire module if matplotlib isn't installed
matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")  # non-interactive backend so tests pass headlessly
import matplotlib.pyplot as plt  # noqa: E402

from swmm_breach import FailureMode, StorageCurve, froehlich, simulate  # noqa: E402
from swmm_breach.uncertainty import ensemble_simulate  # noqa: E402


def _toy_storage() -> StorageCurve:
    return StorageCurve(
        stage_m=np.array([0.0, 5.0, 10.0]),
        volume_m3=np.array([0.0, 1e5, 5e5]),
    )


def test_hydrograph_plot_returns_axes():
    geom = froehlich.predict(5e5, 10.0, 10.0, FailureMode.PIPING)
    hg = simulate(geom, _toy_storage(), 10.0, 10.0, dt_s=10.0, duration_s=3600)
    ax = hg.plot()
    assert ax is not None
    assert len(ax.lines) == 1
    plt.close("all")


def test_hydrograph_plot_accepts_existing_axes():
    geom = froehlich.predict(5e5, 10.0, 10.0, FailureMode.PIPING)
    hg = simulate(geom, _toy_storage(), 10.0, 10.0, dt_s=10.0, duration_s=3600)
    fig, ax = plt.subplots()
    returned = hg.plot(ax=ax)
    assert returned is ax
    plt.close("all")


def test_ensemble_plot_envelope_renders():
    ens = ensemble_simulate(
        storage=_toy_storage(),
        crest_elevation_m=10.0,
        initial_stage_m=10.0,
        volume_m3=5e5,
        height_m=10.0,
        mode=FailureMode.PIPING,
        n_samples=50,
        dt_s=20.0,
        duration_s=3600,
        rng=np.random.default_rng(0),
    )
    ax = ens.plot_envelope()
    # Should have one filled band + median line = at least 1 line + 1 polygon
    assert len(ax.lines) >= 1
    assert len(ax.collections) >= 1
    plt.close("all")


def test_ensemble_plot_envelope_with_realizations_overlay():
    ens = ensemble_simulate(
        storage=_toy_storage(),
        crest_elevation_m=10.0,
        initial_stage_m=10.0,
        volume_m3=5e5,
        height_m=10.0,
        mode=FailureMode.PIPING,
        n_samples=30,
        dt_s=20.0,
        duration_s=3600,
        rng=np.random.default_rng(0),
    )
    ax = ens.plot_envelope(show_realizations=True, n_realizations=10)
    # Median line + 10 realizations = at least 11 lines
    assert len(ax.lines) >= 11
    plt.close("all")
