"""Lawn Lake Dam (1982) regression test -- third validation case.

Lawn Lake was a small earthen embankment dam in Rocky Mountain National
Park, Colorado.  It failed by piping on 15 July 1982, releasing the
~798,500 m^3 reservoir into the Roaring River drainage.  The failure is
documented in the USGS report by Jarrett & Costa (1986) and is one of
the most-cited entries in Wahl's (2004) breach database.

Embankment parameters (from Jarrett & Costa 1986 and Wahl 2004 Table 1):

    Reservoir volume V_w     798,500 m^3
    Breach height h_b         6.4 m
    Failure mode             piping
    Observed peak Q          ~510 m^3/s (Jarrett & Costa 1986 USGS report)
    Observed B_avg            22.2 m
    Observed t_f             ~0.5 hr (1800 s)

This case fills the volume gap between Anson (~10^5 m^3) and Teton
(~10^8 m^3) at ~10^6 m^3, demonstrating that the multi-model ensemble
brackets reference data across nearly four orders of magnitude.
"""

import numpy as np
import pytest

from swmm_breach import FailureMode, StorageCurve
from swmm_breach.uncertainty import ensemble_simulate_multi_model


VOL_M3 = 798_500.0
H_B_M = 6.4
OBS_PEAK_M3S = 510.0   # Jarrett & Costa 1986


def _lawn_lake_storage() -> StorageCurve:
    """Approximate stage-storage for Lawn Lake reservoir.

    Lawn Lake was a roughly oval alpine reservoir; the curve below is a
    reasonable monotonic approximation that integrates to the documented
    full-pool volume of 798,500 m^3 at h = 6.4 m above the breach invert.
    """
    return StorageCurve(
        stage_m=np.array([0.0, 1.5, 3.0, 4.5, 6.4]),
        volume_m3=np.array([0.0, 90_000.0, 250_000.0, 470_000.0, 798_500.0]),
    )


def test_multi_model_ensemble_brackets_observed_lawn_lake_peak():
    """The multi-model 5-95 envelope should bracket the observed
    Jarrett & Costa (1986) peak of ~510 m^3/s."""
    ens = ensemble_simulate_multi_model(
        storage=_lawn_lake_storage(),
        crest_elevation_m=H_B_M,
        initial_stage_m=H_B_M,
        volume_m3=VOL_M3,
        height_m=H_B_M,
        mode=FailureMode.PIPING,
        n_samples=500,
        dt_s=2.0,
        duration_s=3 * 3600,
        rng=np.random.default_rng(20260511),
    )
    p5 = ens.peak_percentile(5)
    p95 = ens.peak_percentile(95)
    assert p5 <= OBS_PEAK_M3S <= p95, (
        f"Observed Lawn Lake peak {OBS_PEAK_M3S:.0f} m^3/s outside "
        f"swmm-breach 5-95 envelope [{p5:.0f}, {p95:.0f}] m^3/s"
    )


def test_lawn_lake_ensemble_median_within_factor_of_3():
    """Loose factor-of-3 tolerance reflects (a) the simplification of
    the storage curve and (b) the larger residual uncertainty at small
    reservoir scales."""
    ens = ensemble_simulate_multi_model(
        storage=_lawn_lake_storage(),
        crest_elevation_m=H_B_M,
        initial_stage_m=H_B_M,
        volume_m3=VOL_M3,
        height_m=H_B_M,
        mode=FailureMode.PIPING,
        n_samples=500,
        dt_s=2.0,
        duration_s=3 * 3600,
        rng=np.random.default_rng(20260511),
    )
    med = ens.peak_percentile(50)
    ratio = med / OBS_PEAK_M3S
    assert 1 / 3 <= ratio <= 3.0, (
        f"Median peak {med:.0f} m^3/s vs observed {OBS_PEAK_M3S:.0f} "
        f"is off by factor {ratio:.2f}"
    )
