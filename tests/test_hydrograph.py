"""End-to-end test of breach growth + level-pool routing on a Teton-scale dam."""

import numpy as np

from swmm_breach import FailureMode, StorageCurve, froehlich, simulate


def teton_storage_curve() -> StorageCurve:
    """Coarse stage-storage approximation for Teton-scale reservoir."""
    return StorageCurve(
        stage_m=np.array([0.0, 20.0, 40.0, 60.0, 80.0, 87.0]),
        volume_m3=np.array([0.0, 12e6, 60e6, 160e6, 290e6, 308e6]),
    )


def test_teton_hydrograph_smoke():
    geom = froehlich.predict(
        volume_m3=308e6,
        height_m=86.9,
        crest_elevation_m=87.0,
        mode=FailureMode.PIPING,
    )
    hg = simulate(
        geometry=geom,
        storage=teton_storage_curve(),
        crest_elevation_m=87.0,
        initial_stage_m=87.0,
        dt_s=10.0,
        duration_s=8 * 3600,
    )
    # Reservoir actually drains
    assert hg.stage_m[-1] < hg.stage_m[0]
    # Peak outflow is large and finite for a Teton-scale dam
    assert 1e4 < hg.peak_outflow_m3s < 5e5
    # Peak occurs after breach has had time to develop
    assert hg.time_to_peak_s > 0.25 * geom.formation_time_s


def test_simulate_conserves_mass_within_tolerance():
    geom = froehlich.predict(
        volume_m3=1e6,
        height_m=10.0,
        crest_elevation_m=10.0,
        mode=FailureMode.OVERTOPPING,
    )
    storage = StorageCurve(
        stage_m=np.array([0.0, 5.0, 10.0]),
        volume_m3=np.array([0.0, 0.4e6, 1.0e6]),
    )
    hg = simulate(
        geometry=geom,
        storage=storage,
        crest_elevation_m=10.0,
        initial_stage_m=10.0,
        dt_s=1.0,
        duration_s=4 * 3600,
    )
    discharged = float(np.trapezoid(hg.outflow_m3s, hg.time_s))
    initial_v = storage.volume_at(10.0)
    final_v = storage.volume_at(hg.stage_m[-1])
    drained = initial_v - final_v
    rel_err = abs(discharged - drained) / drained
    assert rel_err < 0.05
