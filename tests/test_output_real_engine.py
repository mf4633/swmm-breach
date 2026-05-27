"""Validation of the ``.out`` reader against a *real* SWMM-engine output.

Unlike :mod:`test_output`, which round-trips the reader against fixtures
this package writes itself, this module reads
``tests/data/teton_real_engine.out`` -- produced by the unmodified
**EPA SWMM 5.2.4** engine (``runswmm.exe``) routing
``examples/teton_pcswmm_example.inp``. The same file is produced
byte-for-byte by PCSWMM Professional 2D, which embeds the same engine.

The expected values below are the independent ground truth printed in the
companion ``.rpt`` summary, so a match confirms the binary reader agrees
with the engine -- not merely with this package's own writer.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from swmm_breach.output import (
    LinkVariable,
    NodeVariable,
    link_series,
    node_series,
    read_metadata,
)

OUT = Path(__file__).parent / "data" / "teton_real_engine.out"

pytestmark = pytest.mark.skipif(
    not OUT.exists(),
    reason="real-engine fixture missing; run runswmm.exe on the Teton example",
)


def test_metadata_matches_engine_output():
    meta = read_metadata(OUT)
    assert meta.flow_units == "CMS"
    assert meta.n_subcatch == 0
    assert meta.n_nodes == 4
    assert meta.n_links == 3
    assert meta.n_pollutants == 0
    assert meta.n_periods == 360
    assert meta.report_step_s == 60
    assert meta.start_datetime == datetime(2026, 6, 5, 14, 0, 0)
    assert meta.node_ids == ("JN_Toe", "JN_2", "JN_3", "OUT_1")
    assert meta.link_ids == ("C1", "C2", "C3")
    assert meta.error_code == 0


def test_node_depth_matches_rpt_summary():
    # .rpt Node Depth Summary: JN_Toe max depth 32.11 m at 01:08.
    t, depth = node_series(OUT, "JN_Toe", NodeVariable.DEPTH)
    i = int(np.argmax(depth))
    assert depth[i] == pytest.approx(32.11, abs=0.05)
    assert t[i] == pytest.approx(68 * 60, abs=60)  # 01:08 into the run


def test_node_total_inflow_matches_rpt_summary():
    # .rpt Node Inflow Summary: JN_Toe max total inflow 118807.742 CMS.
    _, q = node_series(OUT, "JN_Toe", NodeVariable.TOTAL_INFLOW)
    assert q.max() == pytest.approx(118807.7, rel=1e-3)


def test_link_flow_matches_rpt_summary():
    # .rpt Link Flow Summary: C3 max |flow| 118117.188 CMS.
    _, q = link_series(OUT, "C3", LinkVariable.FLOW)
    assert q.max() == pytest.approx(118117.2, rel=1e-3)


def test_outfall_volume_conserves_reservoir_storage():
    # The routed breach should pass ~the full 308e6 m^3 reservoir through
    # the outfall; integrate C3 flow and check mass balance to a few percent.
    t, q = link_series(OUT, "C3", LinkVariable.FLOW)
    # Trapezoidal integral, written out to stay numpy 1.x / 2.0 agnostic
    # (np.trapz was removed in numpy 2.0).
    volume_m3 = float(np.sum(0.5 * (q[1:] + q[:-1]) * np.diff(t)))
    assert volume_m3 == pytest.approx(308e6, rel=0.05)
