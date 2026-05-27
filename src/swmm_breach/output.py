"""EPA SWMM 5.x ``.out`` binary output file reader (post-processing).

After re-running SWMM with a breach inflow pasted in by
:mod:`swmm_breach.swmm`, this module pulls back the downstream node
depths/flows from the binary output file for inundation reporting.

Format reference
----------------
The ``.out`` layout is documented in the EPA SWMM 5 source (``output.c``)
and Programmer's Toolkit.  All multi-byte values are little-endian.
File structure::

    [opening: 7 ints]                              28 bytes
    [object IDs: n*(int len + chars) each]         variable
    [pollutant units: n_pollutants ints]
    [object properties block]                      variable
    [reporting variables block]
    [start datetime (double) + report step (int)]  12 bytes
    [computed results: n_periods * bytes_per_period]
    [closing: 6 ints]                              last 24 bytes

The closing block carries file offsets to each major section, so the
reader walks the closing block first and then jumps directly to where it
needs to be.

Compatibility
-------------
Targets SWMM 5.1+ output.  The reader is round-tripped against synthetic
fixtures (``tests/test_output.py``) and validated against a real EPA SWMM
5.2.4 engine ``.out`` (``tests/test_output_real_engine.py``).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import IntEnum
from pathlib import Path
from typing import Tuple, Union

import numpy as np

MAGIC = 516114522
SWMM_EPOCH = datetime(1899, 12, 30)

FLOW_UNIT_NAMES = {
    0: "CFS", 1: "GPM", 2: "MGD", 3: "CMS", 4: "LPS", 5: "MLD",
}

# Number of reporting variables per object before pollutants are appended
N_SUBCATCH_VARS_BASE = 8
N_NODE_VARS_BASE = 6
N_LINK_VARS_BASE = 5
N_SYS_VARS = 15


class NodeVariable(IntEnum):
    DEPTH = 0
    HEAD = 1
    VOLUME = 2
    LATERAL_INFLOW = 3
    TOTAL_INFLOW = 4
    FLOODING = 5
    # 6 + i = pollutant i concentration


class LinkVariable(IntEnum):
    FLOW = 0
    DEPTH = 1
    VELOCITY = 2
    VOLUME = 3
    CAPACITY = 4
    # 5 + i = pollutant i concentration


@dataclass(frozen=True)
class OutputMetadata:
    """Header information from a SWMM ``.out`` file."""

    version: int
    flow_units: str
    n_subcatch: int
    n_nodes: int
    n_links: int
    n_pollutants: int
    n_periods: int
    report_step_s: int
    start_datetime: datetime
    subcatch_ids: Tuple[str, ...]
    node_ids: Tuple[str, ...]
    link_ids: Tuple[str, ...]
    pollutant_ids: Tuple[str, ...]
    error_code: int
    output_offset: int


def _read_int(f) -> int:
    return struct.unpack("<i", f.read(4))[0]


def _read_double(f) -> float:
    return struct.unpack("<d", f.read(8))[0]


def _read_id(f) -> str:
    n = _read_int(f)
    return f.read(n).decode("utf-8")


def read_metadata(path: Union[str, Path]) -> OutputMetadata:
    """Parse the header, IDs, and closing block of a SWMM ``.out`` file."""
    path = Path(path)
    size = path.stat().st_size
    with path.open("rb") as f:
        # Closing block (last 24 bytes)
        f.seek(size - 24)
        id_offset = _read_int(f)
        _input_offset = _read_int(f)
        output_offset = _read_int(f)
        n_periods = _read_int(f)
        error_code = _read_int(f)
        magic_end = _read_int(f)
        if magic_end != MAGIC:
            raise ValueError(
                f"End-of-file magic mismatch: {magic_end} != {MAGIC}; "
                "file is not a valid SWMM .out"
            )

        # Opening block
        f.seek(0)
        magic_start = _read_int(f)
        if magic_start != MAGIC:
            raise ValueError(
                f"Start-of-file magic mismatch: {magic_start} != {MAGIC}"
            )
        version = _read_int(f)
        flow_units_code = _read_int(f)
        n_subcatch = _read_int(f)
        n_nodes = _read_int(f)
        n_links = _read_int(f)
        n_pollutants = _read_int(f)

        # Object IDs at id_offset
        f.seek(id_offset)
        subcatch_ids = tuple(_read_id(f) for _ in range(n_subcatch))
        node_ids = tuple(_read_id(f) for _ in range(n_nodes))
        link_ids = tuple(_read_id(f) for _ in range(n_links))
        pollutant_ids = tuple(_read_id(f) for _ in range(n_pollutants))

        # Start datetime + report step are written immediately before the
        # output section (output.c writes them, then captures OutputPosition).
        f.seek(output_offset - 12)
        start_julian = _read_double(f)
        report_step = _read_int(f)
        start_datetime = SWMM_EPOCH + timedelta(days=start_julian)

    return OutputMetadata(
        version=version,
        flow_units=FLOW_UNIT_NAMES.get(flow_units_code, str(flow_units_code)),
        n_subcatch=n_subcatch,
        n_nodes=n_nodes,
        n_links=n_links,
        n_pollutants=n_pollutants,
        n_periods=n_periods,
        report_step_s=report_step,
        start_datetime=start_datetime,
        subcatch_ids=subcatch_ids,
        node_ids=node_ids,
        link_ids=link_ids,
        pollutant_ids=pollutant_ids,
        error_code=error_code,
        output_offset=output_offset,
    )


def _bytes_per_period(meta: OutputMetadata) -> int:
    n_sub_vars = N_SUBCATCH_VARS_BASE + meta.n_pollutants
    n_node_vars = N_NODE_VARS_BASE + meta.n_pollutants
    n_link_vars = N_LINK_VARS_BASE + meta.n_pollutants
    return (
        8  # date double
        + 4 * (
            meta.n_subcatch * n_sub_vars
            + meta.n_nodes * n_node_vars
            + meta.n_links * n_link_vars
            + N_SYS_VARS
        )
    )


def _read_series(
    path: Path,
    meta: OutputMetadata,
    in_period_offset: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """Read a single float per reporting period from a fixed in-period offset."""
    bytes_per_period = _bytes_per_period(meta)
    values = np.empty(meta.n_periods, dtype=np.float32)
    with path.open("rb") as f:
        for p in range(meta.n_periods):
            f.seek(meta.output_offset + p * bytes_per_period + in_period_offset)
            values[p] = struct.unpack("<f", f.read(4))[0]
    times = np.arange(1, meta.n_periods + 1, dtype=float) * meta.report_step_s
    return times, values.astype(float)


def node_series(
    path: Union[str, Path],
    node_name: str,
    variable: Union[NodeVariable, int],
) -> Tuple[np.ndarray, np.ndarray]:
    """Return ``(times_s, values)`` for a node's reported variable.

    ``times_s`` is seconds from simulation start; the first reporting
    period is at ``report_step_s``, matching SWMM's reporting convention.
    """
    path = Path(path)
    meta = read_metadata(path)
    if node_name not in meta.node_ids:
        raise KeyError(
            f"Node {node_name!r} not found; available: {sorted(meta.node_ids)}"
        )
    var_idx = int(variable)
    n_node_vars = N_NODE_VARS_BASE + meta.n_pollutants
    if not 0 <= var_idx < n_node_vars:
        raise ValueError(
            f"Variable index {var_idx} out of range (0..{n_node_vars - 1})"
        )
    node_idx = meta.node_ids.index(node_name)
    n_sub_vars = N_SUBCATCH_VARS_BASE + meta.n_pollutants
    in_period_offset = 8 + 4 * (
        meta.n_subcatch * n_sub_vars + node_idx * n_node_vars + var_idx
    )
    return _read_series(path, meta, in_period_offset)


def link_series(
    path: Union[str, Path],
    link_name: str,
    variable: Union[LinkVariable, int],
) -> Tuple[np.ndarray, np.ndarray]:
    """Return ``(times_s, values)`` for a link's reported variable."""
    path = Path(path)
    meta = read_metadata(path)
    if link_name not in meta.link_ids:
        raise KeyError(
            f"Link {link_name!r} not found; available: {sorted(meta.link_ids)}"
        )
    var_idx = int(variable)
    n_link_vars = N_LINK_VARS_BASE + meta.n_pollutants
    if not 0 <= var_idx < n_link_vars:
        raise ValueError(
            f"Variable index {var_idx} out of range (0..{n_link_vars - 1})"
        )
    link_idx = meta.link_ids.index(link_name)
    n_sub_vars = N_SUBCATCH_VARS_BASE + meta.n_pollutants
    n_node_vars = N_NODE_VARS_BASE + meta.n_pollutants
    in_period_offset = 8 + 4 * (
        meta.n_subcatch * n_sub_vars
        + meta.n_nodes * n_node_vars
        + link_idx * n_link_vars + var_idx
    )
    return _read_series(path, meta, in_period_offset)
