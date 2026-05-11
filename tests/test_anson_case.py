"""Anson County Lower Lagoon (ANSON-057) regression test.

Validates the swmm-breach probabilistic ensemble against an
independent HEC-RAS 6.6 2D unsteady analysis of the same scenario,
performed for the Class C -> Class A hazard reclassification submittal
to the NC Dam Safety Program (April 2026).

Embankment parameters from the Anson County WTP Sludge Lagoon Dams
O&M Plan (May 2026), based on the 2023 post-rehabilitation as-built
survey.
"""

import numpy as np

from swmm_breach import FailureMode, StorageCurve
from swmm_breach.uncertainty import ensemble_simulate


# Lower Lagoon (ANSON-057), NAVD88 elevations converted to metres
NP_ELEV_M = 458.89 * 0.3048
CREST_ELEV_M = 463.5 * 0.3048
TOE_ELEV_M = CREST_ELEV_M - 25.0 * 0.3048           # structural height 25 ft
VOL_NP_M3 = 64.0 * 1233.48                           # 64 ac-ft
VOL_CREST_M3 = 111.0 * 1233.48
BREACH_HEIGHT_M = NP_ELEV_M - TOE_ELEV_M             # 6.21 m

# Reference: HEC-RAS 6.6 2D unsteady, Lower-piping-at-NP scenario
HEC_RAS_PEAK_CFS = 4301.0
HEC_RAS_PEAK_M3S = HEC_RAS_PEAK_CFS / 35.31466621


def _lower_lagoon_storage() -> StorageCurve:
    return StorageCurve(
        stage_m=np.array([TOE_ELEV_M, 136.5, NP_ELEV_M, CREST_ELEV_M]),
        volume_m3=np.array([0.0, 10_000.0, VOL_NP_M3, VOL_CREST_M3]),
    )


def test_ensemble_brackets_hec_ras_peak():
    """The 5-95 percentile peak envelope should contain the HEC-RAS
    reference peak of 121.8 m^3/s (4,301 cfs)."""
    ens = ensemble_simulate(
        storage=_lower_lagoon_storage(),
        crest_elevation_m=NP_ELEV_M,
        initial_stage_m=NP_ELEV_M,
        volume_m3=VOL_NP_M3,
        height_m=BREACH_HEIGHT_M,
        mode=FailureMode.PIPING,
        n_samples=500,
        dt_s=2.0,
        duration_s=2 * 3600,
        rng=np.random.default_rng(20260511),
    )
    p5 = ens.peak_percentile(5)
    p95 = ens.peak_percentile(95)
    assert p5 <= HEC_RAS_PEAK_M3S <= p95, (
        f"HEC-RAS reference peak {HEC_RAS_PEAK_M3S:.1f} m^3/s ({HEC_RAS_PEAK_CFS:.0f} cfs) "
        f"is outside swmm-breach 5-95 envelope [{p5:.1f}, {p95:.1f}] m^3/s"
    )


def test_ensemble_median_within_factor_of_2_of_hec_ras():
    """Median of the ensemble should be within a factor of 2 of HEC-RAS,
    a common engineering tolerance for breach-model agreement."""
    ens = ensemble_simulate(
        storage=_lower_lagoon_storage(),
        crest_elevation_m=NP_ELEV_M,
        initial_stage_m=NP_ELEV_M,
        volume_m3=VOL_NP_M3,
        height_m=BREACH_HEIGHT_M,
        mode=FailureMode.PIPING,
        n_samples=500,
        dt_s=2.0,
        duration_s=2 * 3600,
        rng=np.random.default_rng(20260511),
    )
    med = ens.peak_percentile(50)
    ratio = med / HEC_RAS_PEAK_M3S
    assert 0.5 <= ratio <= 2.0, (
        f"Median ensemble peak {med:.1f} m^3/s vs HEC-RAS {HEC_RAS_PEAK_M3S:.1f} "
        f"is off by factor {ratio:.2f}"
    )
