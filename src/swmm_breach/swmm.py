"""EPA SWMM 5.x ``.inp`` integration: read storage curves, write inflow blocks.

Only the sections needed for breach work are parsed:

- ``[STORAGE]`` — storage nodes with ``SHAPE = TABULAR`` (curve-based);
  functional shapes raise NotImplementedError.
- ``[CURVES]`` — STORAGE-type stage-storage curves referenced by storage nodes.

The output of :func:`format_inflows_block` is a string that can be pasted
directly into an ``.inp`` file's ``[TIMESERIES]`` and ``[INFLOWS]`` sections,
or written to a separate file referenced via ``TIMESERIES <name> FILE``.

References
----------
Rossman, L. A. (2017). Storm Water Management Model Reference Manual,
Volume II - Hydraulics. EPA/600/R-17/111.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from .hydrograph import Hydrograph
from .reservoir import StorageCurve

CMS_TO_CFS = 35.31466621266132  # 1 m^3/s in ft^3/s


@dataclass(frozen=True)
class StorageNode:
    """A SWMM ``[STORAGE]`` row (TABULAR shape only)."""

    name: str
    invert_elevation: float
    max_depth: float
    initial_depth: float
    curve_name: str


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_SECTION_RE = re.compile(r"^\s*\[(?P<name>[A-Z_][A-Z_0-9]*)\]\s*$", re.IGNORECASE)


def read_sections(path: str | Path) -> Dict[str, List[str]]:
    """Read a SWMM ``.inp`` file and return ``{section_name_upper: [lines]}``.

    Comment lines (``;``) and blank lines are stripped. Section names are
    upper-cased. Lines preserve original whitespace-separated tokens.
    """
    sections: Dict[str, List[str]] = {}
    current: str | None = None
    for raw in Path(path).read_text().splitlines():
        line = raw.split(";", 1)[0].rstrip()
        if not line.strip():
            continue
        m = _SECTION_RE.match(line)
        if m:
            current = m.group("name").upper()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line.strip())
    return sections


def parse_storage_nodes(lines: List[str]) -> Dict[str, StorageNode]:
    """Parse the body lines of a ``[STORAGE]`` section.

    Only ``SHAPE = TABULAR`` is supported; other shapes raise
    :class:`NotImplementedError` so callers fail loudly rather than silently
    misinterpreting a functional curve.
    """
    out: Dict[str, StorageNode] = {}
    for line in lines:
        toks = line.split()
        if len(toks) < 6:
            continue
        name, elev, maxd, initd, shape = toks[:5]
        if shape.upper() != "TABULAR":
            raise NotImplementedError(
                f"Storage node {name!r} uses SHAPE={shape!r}; "
                "only TABULAR is supported in v0.2."
            )
        out[name] = StorageNode(
            name=name,
            invert_elevation=float(elev),
            max_depth=float(maxd),
            initial_depth=float(initd),
            curve_name=toks[5],
        )
    return out


def parse_curves(lines: List[str]) -> Dict[str, List[Tuple[float, float]]]:
    """Parse a ``[CURVES]`` section into ``{curve_name: [(x, y), ...]}``.

    Each curve's first row carries a Type token (e.g. ``STORAGE``);
    subsequent rows for the same curve omit it. The Type itself is not
    returned — caller is expected to know which curve they want.
    """
    out: Dict[str, List[Tuple[float, float]]] = {}
    for line in lines:
        toks = line.split()
        if len(toks) < 3:
            continue
        name = toks[0]
        # Detect optional Type token in second position (alphabetic, non-numeric)
        try:
            float(toks[1])
            x, y = float(toks[1]), float(toks[2])
        except ValueError:
            x, y = float(toks[2]), float(toks[3])
        out.setdefault(name, []).append((x, y))
    return out


def load_storage_curve(
    inp_path: str | Path, node_name: str
) -> Tuple[StorageCurve, StorageNode]:
    """Build a :class:`StorageCurve` from a named storage node in an ``.inp``.

    The curve's stage axis is shifted by the node's invert elevation, so
    ``StorageCurve.stage_m`` is in absolute elevation units (matching the
    invert + depth convention used elsewhere in swmm-breach).
    """
    sections = read_sections(inp_path)
    if "STORAGE" not in sections:
        raise KeyError(f"No [STORAGE] section in {inp_path}")
    if "CURVES" not in sections:
        raise KeyError(f"No [CURVES] section in {inp_path}")

    nodes = parse_storage_nodes(sections["STORAGE"])
    if node_name not in nodes:
        raise KeyError(
            f"Storage node {node_name!r} not found; "
            f"available: {sorted(nodes)}"
        )
    node = nodes[node_name]

    curves = parse_curves(sections["CURVES"])
    if node.curve_name not in curves:
        raise KeyError(
            f"Curve {node.curve_name!r} (referenced by {node_name!r}) "
            f"not found in [CURVES]"
        )
    points = sorted(curves[node.curve_name], key=lambda p: p[0])
    depth = np.array([p[0] for p in points], dtype=float)
    volume = np.array([p[1] for p in points], dtype=float)

    return (
        StorageCurve(stage_m=node.invert_elevation + depth, volume_m3=volume),
        node,
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _q_in_units(q_cms: np.ndarray, units: str) -> np.ndarray:
    if units.upper() == "CMS":
        return q_cms
    if units.upper() == "CFS":
        return q_cms * CMS_TO_CFS
    raise ValueError(f"units must be 'CMS' or 'CFS', got {units!r}")


def format_inflows_block(
    hydrograph: Hydrograph,
    node_name: str,
    timeseries_name: str,
    start_datetime: datetime,
    units: str = "CMS",
    decimate: int = 1,
) -> str:
    """Format a hydrograph as a paste-ready SWMM ``.inp`` snippet.

    Parameters
    ----------
    hydrograph
        Output of :func:`swmm_breach.simulate`. Internally m^3/s.
    node_name
        The SWMM node receiving the inflow (typically ``Outfall`` downstream
        of the breached reservoir).
    timeseries_name
        Name to assign the new time series.
    start_datetime
        Real-world datetime corresponding to ``hydrograph.time_s[0] == 0``.
    units
        ``"CMS"`` (m^3/s) or ``"CFS"`` (ft^3/s); must match the project's
        ``FLOW_UNITS`` in ``[OPTIONS]``. swmm-breach is internally CMS.
    decimate
        Write every Nth point; useful when ``dt_s`` is small relative to
        the SWMM ``ROUTING_STEP``. Defaults to 1 (no decimation).

    Returns
    -------
    str
        A snippet starting with ``[TIMESERIES]`` and ``[INFLOWS]`` headers,
        ready to append to a ``.inp`` file.
    """
    if decimate < 1:
        raise ValueError("decimate must be >= 1")

    q = _q_in_units(hydrograph.outflow_m3s, units)
    t = hydrograph.time_s

    lines: List[str] = []
    lines.append("[TIMESERIES]")
    lines.append(";;Name           Date       Time       Value")
    lines.append(";;-------------- ---------- ---------- ----------")
    for i in range(0, len(t), decimate):
        ts = start_datetime + timedelta(seconds=float(t[i]))
        lines.append(
            f"{timeseries_name:<16} "
            f"{ts.strftime('%m/%d/%Y')} "
            f"{ts.strftime('%H:%M:%S')}  "
            f"{q[i]:.4f}"
        )
    lines.append("")
    lines.append("[INFLOWS]")
    lines.append(";;Node           Constituent      TimeSeries       Type     Mfactor  Sfactor  Baseline Pattern")
    lines.append(";;-------------- ---------------- ---------------- -------- -------- -------- -------- --------")
    lines.append(
        f"{node_name:<16} FLOW             {timeseries_name:<16} "
        f"FLOW     1.0      1.0"
    )
    lines.append("")
    return "\n".join(lines)
