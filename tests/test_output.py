"""Round-trip tests for the SWMM ``.out`` binary reader.

Fixture .out files are generated in-test from the documented SWMM 5
format (see ``output.c`` in the EPA SWMM source).  Reader and writer
are independently coded against the same spec, so a successful
round-trip is evidence the reader matches the spec — but is *not* a
substitute for validation against an actual SWMM-engine-produced .out.
"""

import struct
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pytest

from swmm_breach.output import (
    LinkVariable,
    NodeVariable,
    SWMM_EPOCH,
    link_series,
    node_series,
    read_metadata,
)

MAGIC = 516114522


def _write_test_out(
    path: Path,
    node_id: str,
    link_id: str,
    node_depths: List[float],
    link_flows: List[float],
    *,
    report_step: int = 60,
    flow_units_code: int = 3,  # CMS
    start: datetime = datetime(2026, 6, 5, 14, 0, 0),
) -> None:
    """Write a minimal valid SWMM 5 .out file: 0 subcatchments, 1 node,
    1 link, 0 pollutants.

    The fixture is the simplest .out that exercises every offset
    calculation the reader has to perform.
    """
    assert len(node_depths) == len(link_flows)
    n_periods = len(node_depths)
    n_subcatch, n_nodes, n_links, n_pollutants = 0, 1, 1, 0

    start_julian = (start - SWMM_EPOCH).total_seconds() / 86400.0

    with path.open("wb") as f:
        # ---- Opening (7 ints) ----
        f.write(struct.pack("<i", MAGIC))
        f.write(struct.pack("<i", 51000))            # version
        f.write(struct.pack("<i", flow_units_code))
        f.write(struct.pack("<i", n_subcatch))
        f.write(struct.pack("<i", n_nodes))
        f.write(struct.pack("<i", n_links))
        f.write(struct.pack("<i", n_pollutants))

        # ---- Object ID names ----
        id_offset = f.tell()
        # (no subcatchments)
        for name in [node_id]:
            b = name.encode("utf-8")
            f.write(struct.pack("<i", len(b)) + b)
        for name in [link_id]:
            b = name.encode("utf-8")
            f.write(struct.pack("<i", len(b)) + b)
        # (no pollutants)

        # Pollutant units (n_pollutants ints) — zero of them here

        # ---- Object properties ----
        input_offset = f.tell()

        # Subcatch property header (zero subcatchments, but header still written)
        f.write(struct.pack("<i", 1))                 # n_subcatch_props
        f.write(struct.pack("<i", 1))                 # property code (AREA)

        # Node properties: type, invert_elev, max_depth
        f.write(struct.pack("<i", 3))                 # n_node_props
        f.write(struct.pack("<iii", 0, 1, 2))
        f.write(struct.pack("<fff", 0.0, 100.0, 10.0))  # JUNCTION, invert, depth

        # Link properties: type, offset1, offset2, max_depth, length
        f.write(struct.pack("<i", 5))                 # n_link_props
        f.write(struct.pack("<iiiii", 0, 1, 2, 3, 4))
        f.write(struct.pack("<fffff", 0.0, 0.0, 0.0, 5.0, 100.0))

        # ---- Reporting variables ----
        f.write(struct.pack("<i", 8))                 # subcatch vars
        f.write(struct.pack("<8i", *range(8)))
        f.write(struct.pack("<i", 6))                 # node vars
        f.write(struct.pack("<6i", *range(6)))
        f.write(struct.pack("<i", 5))                 # link vars
        f.write(struct.pack("<5i", *range(5)))
        f.write(struct.pack("<i", 15))                # system vars
        f.write(struct.pack("<15i", *range(15)))

        # ---- Start datetime + report step ----
        f.write(struct.pack("<d", start_julian))
        f.write(struct.pack("<i", report_step))

        # ---- Computed results ----
        output_offset = f.tell()
        for i in range(n_periods):
            current_julian = start_julian + (i + 1) * report_step / 86400.0
            f.write(struct.pack("<d", current_julian))
            # 0 subcatchments => no subcatch values
            # Node: depth, head, volume, lat_inflow, total_inflow, flooding
            d = node_depths[i]
            f.write(struct.pack("<6f", d, d + 100.0, d * 50.0, 0.0, 0.0, 0.0))
            # Link: flow, depth, velocity, volume, capacity
            q = link_flows[i]
            f.write(struct.pack("<5f", q, 0.5, 1.0, 100.0, 0.5))
            # 15 system variables (all zero)
            f.write(struct.pack("<15f", *([0.0] * 15)))

        # ---- Closing (6 ints) ----
        f.write(struct.pack("<i", id_offset))
        f.write(struct.pack("<i", input_offset))
        f.write(struct.pack("<i", output_offset))
        f.write(struct.pack("<i", n_periods))
        f.write(struct.pack("<i", 0))                  # error code
        f.write(struct.pack("<i", MAGIC))


@pytest.fixture
def fixture_out(tmp_path) -> Tuple[Path, List[float], List[float]]:
    path = tmp_path / "test.out"
    depths = [0.0, 1.0, 2.5, 4.0, 3.0, 2.0, 1.0, 0.5, 0.2, 0.0]
    flows = [0.0, 5.0, 50.0, 120.0, 80.0, 40.0, 20.0, 10.0, 5.0, 1.0]
    _write_test_out(path, "DownstreamJN", "Outfall_Pipe", depths, flows,
                    report_step=60)
    return path, depths, flows


def test_read_metadata_recovers_header_fields(fixture_out):
    path, _, _ = fixture_out
    meta = read_metadata(path)
    assert meta.version == 51000
    assert meta.flow_units == "CMS"
    assert meta.n_subcatch == 0
    assert meta.n_nodes == 1
    assert meta.n_links == 1
    assert meta.n_pollutants == 0
    assert meta.n_periods == 10
    assert meta.report_step_s == 60
    assert meta.node_ids == ("DownstreamJN",)
    assert meta.link_ids == ("Outfall_Pipe",)
    assert meta.error_code == 0
    assert meta.start_datetime == datetime(2026, 6, 5, 14, 0, 0)


def test_node_depth_series_matches_written_values(fixture_out):
    path, depths, _ = fixture_out
    times, vals = node_series(path, "DownstreamJN", NodeVariable.DEPTH)
    np.testing.assert_allclose(vals, depths, atol=1e-5)
    np.testing.assert_array_equal(times, np.arange(1, 11) * 60.0)


def test_node_head_series_matches_written_values(fixture_out):
    path, depths, _ = fixture_out
    _, vals = node_series(path, "DownstreamJN", NodeVariable.HEAD)
    np.testing.assert_allclose(vals, [d + 100.0 for d in depths], atol=1e-4)


def test_link_flow_series_matches_written_values(fixture_out):
    path, _, flows = fixture_out
    times, vals = link_series(path, "Outfall_Pipe", LinkVariable.FLOW)
    np.testing.assert_allclose(vals, flows, atol=1e-5)
    np.testing.assert_array_equal(times, np.arange(1, 11) * 60.0)


def test_unknown_node_raises(fixture_out):
    path, _, _ = fixture_out
    with pytest.raises(KeyError, match="not found"):
        node_series(path, "Nope", NodeVariable.DEPTH)


def test_unknown_link_raises(fixture_out):
    path, _, _ = fixture_out
    with pytest.raises(KeyError, match="not found"):
        link_series(path, "Nope", LinkVariable.FLOW)


def test_out_of_range_variable_raises(fixture_out):
    path, _, _ = fixture_out
    with pytest.raises(ValueError, match="out of range"):
        node_series(path, "DownstreamJN", 99)


def test_corrupt_magic_raises(tmp_path):
    p = tmp_path / "corrupt.out"
    p.write_bytes(b"\x00" * 200)
    with pytest.raises(ValueError, match="magic"):
        read_metadata(p)


def test_us_flow_units_recovered(tmp_path):
    p = tmp_path / "cfs.out"
    _write_test_out(p, "N", "L", [1.0, 2.0], [10.0, 20.0],
                    flow_units_code=0)  # CFS
    meta = read_metadata(p)
    assert meta.flow_units == "CFS"
