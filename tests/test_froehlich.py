"""Validate Froehlich (2008) predictions against the Teton Dam failure (1976).

Observed values from the Wahl (2004) USBR breach-database compilation:

    V_w at failure:    308 x 10^6 m^3
    h_b (breach):       86.9 m
    Failure mode:      piping
    B_avg observed:    151 m
    t_f observed:      1.25 hr (4500 s)
"""

import math

import pytest

from swmm_breach import froehlich
from swmm_breach.breach import FailureMode


TETON_VOLUME_M3 = 308e6
TETON_HEIGHT_M = 86.9
TETON_OBSERVED_BAVG_M = 151.0
TETON_OBSERVED_TF_S = 4500.0
TETON_TOL = 0.25  # 25 % is the practical accuracy of empirical breach regressions


def test_teton_breach_width_within_tolerance():
    predicted = froehlich.average_breach_width(
        TETON_VOLUME_M3, TETON_HEIGHT_M, FailureMode.PIPING
    )
    rel_err = abs(predicted - TETON_OBSERVED_BAVG_M) / TETON_OBSERVED_BAVG_M
    assert rel_err < TETON_TOL, (
        f"Predicted B_avg={predicted:.1f} m vs observed "
        f"{TETON_OBSERVED_BAVG_M:.1f} m (rel err {rel_err:.1%})"
    )


def test_teton_formation_time_within_tolerance():
    predicted = froehlich.formation_time(TETON_VOLUME_M3, TETON_HEIGHT_M)
    rel_err = abs(predicted - TETON_OBSERVED_TF_S) / TETON_OBSERVED_TF_S
    assert rel_err < TETON_TOL, (
        f"Predicted t_f={predicted:.0f} s vs observed "
        f"{TETON_OBSERVED_TF_S:.0f} s (rel err {rel_err:.1%})"
    )


def test_overtopping_K_factor_is_1p3_times_piping():
    pip = froehlich.average_breach_width(1e7, 30, FailureMode.PIPING)
    over = froehlich.average_breach_width(1e7, 30, FailureMode.OVERTOPPING)
    assert math.isclose(over / pip, 1.3, rel_tol=1e-9)


def test_predict_returns_full_geometry():
    geom = froehlich.predict(
        volume_m3=1e7,
        height_m=30,
        crest_elevation_m=100,
        mode=FailureMode.OVERTOPPING,
    )
    assert geom.bottom_width_m > 0
    assert geom.formation_time_s > 0
    assert geom.invert_elevation_m == pytest.approx(70.0)
    assert geom.side_slope_h_per_v == 1.0
    assert geom.height_m == 30


def test_side_slope_overtopping_steeper_than_piping():
    assert froehlich.side_slope(FailureMode.OVERTOPPING) == 1.0
    assert froehlich.side_slope(FailureMode.PIPING) == 0.7
