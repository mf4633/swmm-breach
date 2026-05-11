"""Tests for storage curve and breach outflow helpers."""

import numpy as np
import pytest

from swmm_breach.reservoir import StorageCurve, trapezoidal_breach_outflow


def test_storage_curve_round_trip():
    sc = StorageCurve(
        stage_m=np.array([0.0, 1.0, 2.0, 3.0]),
        volume_m3=np.array([0.0, 100.0, 400.0, 900.0]),
    )
    assert sc.volume_at(2.0) == pytest.approx(400.0)
    assert sc.stage_at(400.0) == pytest.approx(2.0)


def test_storage_curve_rejects_non_monotonic():
    with pytest.raises(ValueError):
        StorageCurve(
            stage_m=np.array([0.0, 1.0, 0.5]),
            volume_m3=np.array([0.0, 100.0, 50.0]),
        )


def test_breach_outflow_zero_or_negative_head():
    assert trapezoidal_breach_outflow(0.0, 10.0, 1.0) == 0.0
    assert trapezoidal_breach_outflow(-1.0, 10.0, 1.0) == 0.0


def test_breach_outflow_grows_monotonically_with_head():
    qs = [trapezoidal_breach_outflow(h, 10.0, 1.0) for h in (1.0, 2.0, 3.0, 5.0)]
    assert qs == sorted(qs)
    assert all(q > 0 for q in qs)


def test_breach_outflow_grows_with_bottom_width():
    q_narrow = trapezoidal_breach_outflow(2.0, 5.0, 1.0)
    q_wide = trapezoidal_breach_outflow(2.0, 50.0, 1.0)
    assert q_wide > q_narrow
