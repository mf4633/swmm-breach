"""Round-trip tests for the SWMM ``.inp`` integration."""

from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from swmm_breach import FailureMode, froehlich, simulate
from swmm_breach.swmm import (
    CMS_TO_CFS,
    format_inflows_block,
    load_storage_curve,
    parse_curves,
    parse_storage_nodes,
    read_sections,
)


FIXTURE = Path(__file__).parent / "data" / "teton_minimal.inp"


def test_read_sections_finds_expected_blocks():
    sections = read_sections(FIXTURE)
    assert "STORAGE" in sections
    assert "CURVES" in sections
    assert "OPTIONS" in sections


def test_parse_storage_node():
    sections = read_sections(FIXTURE)
    nodes = parse_storage_nodes(sections["STORAGE"])
    assert "TetonRes" in nodes
    n = nodes["TetonRes"]
    assert n.invert_elevation == 900.0
    assert n.max_depth == 87.0
    assert n.curve_name == "TetonStorage"


def test_parse_curve_handles_type_token_on_first_row_only():
    sections = read_sections(FIXTURE)
    curves = parse_curves(sections["CURVES"])
    assert "TetonStorage" in curves
    pts = curves["TetonStorage"]
    # 6 points, first is (0, 0), last is (87, 308e6)
    assert len(pts) == 6
    assert pts[0] == (0.0, 0.0)
    assert pts[-1] == (87.0, 308e6)


def test_load_storage_curve_applies_invert_offset():
    sc, node = load_storage_curve(FIXTURE, "TetonRes")
    # Stages should be in absolute elevation, offset by invert (900 m)
    assert sc.stage_m[0] == pytest.approx(900.0)
    assert sc.stage_m[-1] == pytest.approx(987.0)
    assert sc.volume_at(987.0) == pytest.approx(308e6)
    assert node.name == "TetonRes"


def test_load_storage_curve_unknown_node_raises():
    with pytest.raises(KeyError, match="not found"):
        load_storage_curve(FIXTURE, "NoSuchNode")


def test_format_inflows_block_round_trip_with_simulate():
    sc, node = load_storage_curve(FIXTURE, "TetonRes")
    crest = node.invert_elevation + node.max_depth
    geom = froehlich.predict(
        volume_m3=sc.volume_at(crest),
        height_m=node.max_depth,
        crest_elevation_m=crest,
        mode=FailureMode.PIPING,
    )
    hg = simulate(
        geometry=geom,
        storage=sc,
        crest_elevation_m=crest,
        initial_stage_m=crest,
        dt_s=10.0,
        duration_s=2 * 3600,
    )
    block = format_inflows_block(
        hg,
        node_name="DownstreamOutfall",
        timeseries_name="TS_TetonBreach",
        start_datetime=datetime(2026, 6, 5, 14, 0, 0),
        units="CMS",
        decimate=6,  # write every minute when dt=10s
    )
    assert "[TIMESERIES]" in block
    assert "[INFLOWS]" in block
    assert "TS_TetonBreach" in block
    assert "DownstreamOutfall" in block
    assert "06/05/2026" in block
    # First data row should be at 14:00:00 with zero flow (pre-breach growth)
    assert "14:00:00" in block


def test_format_inflows_block_cfs_unit_conversion():
    """Verify CFS conversion factor matches CMS_TO_CFS exactly."""
    sc, node = load_storage_curve(FIXTURE, "TetonRes")
    crest = node.invert_elevation + node.max_depth
    geom = froehlich.predict(
        volume_m3=sc.volume_at(crest),
        height_m=node.max_depth,
        crest_elevation_m=crest,
        mode=FailureMode.PIPING,
    )
    hg = simulate(
        geometry=geom,
        storage=sc,
        crest_elevation_m=crest,
        initial_stage_m=crest,
        dt_s=10.0,
        duration_s=600.0,
    )
    cms_block = format_inflows_block(
        hg, "N", "TS", datetime(2026, 1, 1), units="CMS"
    )
    cfs_block = format_inflows_block(
        hg, "N", "TS", datetime(2026, 1, 1), units="CFS"
    )
    # Pull peak value from each block
    def peak(block: str) -> float:
        return max(
            float(line.split()[-1])
            for line in block.splitlines()
            if line.startswith("TS ") and len(line.split()) >= 4
        )
    assert peak(cfs_block) == pytest.approx(peak(cms_block) * CMS_TO_CFS, rel=1e-6)


def test_format_inflows_block_rejects_unknown_units():
    sc, node = load_storage_curve(FIXTURE, "TetonRes")
    crest = node.invert_elevation + node.max_depth
    geom = froehlich.predict(
        volume_m3=sc.volume_at(crest),
        height_m=node.max_depth,
        crest_elevation_m=crest,
        mode=FailureMode.PIPING,
    )
    hg = simulate(
        geometry=geom,
        storage=sc,
        crest_elevation_m=crest,
        initial_stage_m=crest,
        dt_s=60.0,
        duration_s=600.0,
    )
    with pytest.raises(ValueError, match="CMS.*CFS"):
        format_inflows_block(hg, "N", "TS", datetime(2026, 1, 1), units="GPM")


def test_functional_storage_shape_raises_not_implemented(tmp_path):
    inp = tmp_path / "func.inp"
    inp.write_text(
        "[STORAGE]\n"
        "FuncRes 100 10 5 FUNCTIONAL 1000 0.5 0\n"
    )
    sections = read_sections(inp)
    with pytest.raises(NotImplementedError, match="TABULAR"):
        parse_storage_nodes(sections["STORAGE"])
