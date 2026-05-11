"""Validate Froehlich (1995) implementation against the Teton Dam (1976)."""

import math

import pytest

from swmm_breach import froehlich_1995
from swmm_breach.breach import FailureMode

TETON_VOLUME_M3 = 308e6
TETON_HEIGHT_M = 86.9
TETON_OBSERVED_BAVG_M = 151.0
TETON_OBSERVED_TF_S = 4500.0


def test_teton_breach_width_within_50_percent():
    """The 1995 regression has wider residuals than the 2008 update;
    a 50% tolerance reflects its larger published standard error."""
    predicted = froehlich_1995.average_breach_width(
        TETON_VOLUME_M3, TETON_HEIGHT_M, FailureMode.PIPING
    )
    rel_err = abs(predicted - TETON_OBSERVED_BAVG_M) / TETON_OBSERVED_BAVG_M
    assert rel_err < 0.50, (
        f"Predicted B_avg={predicted:.1f} m vs observed "
        f"{TETON_OBSERVED_BAVG_M:.1f} m (rel err {rel_err:.1%})"
    )


def test_teton_formation_time_within_50_percent():
    predicted = froehlich_1995.formation_time(TETON_VOLUME_M3, TETON_HEIGHT_M)
    rel_err = abs(predicted - TETON_OBSERVED_TF_S) / TETON_OBSERVED_TF_S
    assert rel_err < 0.50, (
        f"Predicted t_f={predicted:.0f} s vs observed "
        f"{TETON_OBSERVED_TF_S:.0f} s (rel err {rel_err:.1%})"
    )


def test_overtopping_K_factor_is_1p4_times_piping():
    pip = froehlich_1995.average_breach_width(1e7, 30, FailureMode.PIPING)
    over = froehlich_1995.average_breach_width(1e7, 30, FailureMode.OVERTOPPING)
    assert math.isclose(over / pip, 1.4, rel_tol=1e-9)


def test_predict_returns_full_geometry():
    geom = froehlich_1995.predict(
        volume_m3=1e7, height_m=30,
        crest_elevation_m=100, mode=FailureMode.OVERTOPPING,
    )
    assert geom.bottom_width_m > 0
    assert geom.formation_time_s > 0
    assert geom.invert_elevation_m == pytest.approx(70.0)
    assert geom.side_slope_h_per_v == 0.9


def test_2008_and_1995_disagree_meaningfully_on_teton():
    """The two Froehlich generations should give materially different
    predictions; otherwise multi-model sampling has no information value."""
    from swmm_breach import froehlich
    b08 = froehlich.average_breach_width(
        TETON_VOLUME_M3, TETON_HEIGHT_M, FailureMode.PIPING
    )
    b95 = froehlich_1995.average_breach_width(
        TETON_VOLUME_M3, TETON_HEIGHT_M, FailureMode.PIPING
    )
    rel_diff = abs(b08 - b95) / b08
    assert rel_diff > 0.10, (
        f"Froehlich 2008 ({b08:.0f}) and 1995 ({b95:.0f}) too similar "
        f"on Teton ({rel_diff:.1%}); multi-model uncertainty has no "
        f"information content"
    )
