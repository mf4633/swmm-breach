"""Generate a runnable PCSWMM/SWMM ``.inp`` for the Anson Lower Lagoon case.

US customary units (cfs / feet) -- the natural units for the underlying
NC Dam Safety reclassification project, and for the PCSWMM/CHI readership.

This is the applied companion to ``build_teton_pcswmm.py``: ANSON-057
(Lower Lagoon, piping at normal pool) is a real engagement originally
analyzed in HEC-RAS 6.6 (2D unsteady), peak breach Q = 4,301 cfs. Here the
Froehlich (2008) breach is routed level-pool offline by swmm-breach, then
applied as an ``[INFLOWS]`` time series at the dam toe and conveyed down a
trapezoidal channel to a free outfall -- a workflow PCSWMM cannot do
natively.

swmm-breach is internally SI, so the breach is computed in meters and the
hydrograph is emitted in cfs via ``format_inflows_block(units="CFS")``;
the downstream network is built directly in feet to match ``FLOW_UNITS CFS``.

Run from the repo root with the project venv:

    .venv\\Scripts\\python.exe examples\\build_anson_pcswmm.py
"""

from datetime import datetime
from pathlib import Path

import numpy as np

from swmm_breach import FailureMode, StorageCurve, froehlich, simulate
from swmm_breach.swmm import format_inflows_block

HERE = Path(__file__).resolve().parent
OUT_INP = HERE / "anson_pcswmm_example.inp"

START = datetime(2026, 6, 5, 14, 0, 0)
M_PER_FT = 0.3048
CMS_TO_CFS = 35.31466621266132

# ---- Embankment parameters (NAVD88 feet; from the 2023 as-built survey) --
CREST_FT = 463.5
NP_FT = 458.89
STRUCT_HEIGHT_FT = 25.0
TOE_FT = CREST_FT - STRUCT_HEIGHT_FT          # 438.5 ft
BREACH_HEIGHT_FT = NP_FT - TOE_FT             # 20.39 ft
VOL_NP_ACFT = 64.0
HEC_RAS_PEAK_CFS = 4301.0

# ---- Breach + routing, computed in SI ------------------------------------
NP_M = NP_FT * M_PER_FT
TOE_M = TOE_FT * M_PER_FT
BREACH_HEIGHT_M = NP_M - TOE_M
VOL_NP_M3 = VOL_NP_ACFT * 1233.48
VOL_CREST_M3 = 111.0 * 1233.48

storage = StorageCurve(
    stage_m=np.array([TOE_M, 136.5, NP_M, CREST_FT * M_PER_FT]),
    volume_m3=np.array([0.0, 10_000.0, VOL_NP_M3, VOL_CREST_M3]),
)

geom = froehlich.predict(
    volume_m3=VOL_NP_M3,
    height_m=BREACH_HEIGHT_M,
    crest_elevation_m=NP_M,            # piping develops from NP downward
    mode=FailureMode.PIPING,
)
hg = simulate(
    geometry=geom,
    storage=storage,
    crest_elevation_m=NP_M,
    initial_stage_m=NP_M,
    dt_s=2.0,
    duration_s=2 * 3600,
)

peak_cfs = hg.peak_outflow_m3s * CMS_TO_CFS
print(f"Breach B_avg      : {geom.bottom_width_m / M_PER_FT:.1f} ft")
print(f"Formation time    : {geom.formation_time_s/60:.1f} min")
print(f"Peak outflow      : {peak_cfs:,.0f} cfs at {hg.time_to_peak_s/60:.1f} min")
print(f"HEC-RAS reference : {HEC_RAS_PEAK_CFS:,.0f} cfs")

# ---- INFLOWS / TIMESERIES block in cfs -----------------------------------
inflow_block = format_inflows_block(
    hg,
    node_name="JN_Toe",
    timeseries_name="TS_AnsonBreach",
    start_datetime=START,
    units="CFS",
    decimate=5,                       # dt_s=2 -> one row per 10 s
)

# ---- Downstream routing network (feet) -----------------------------------
# Trapezoidal channel sized to convey the breach peak: 40 ft base, 2H:1V
# sides, 15 ft deep. Toe at the structural toe (438.5 ft NAVD88), sloping
# ~0.003 over three 500 ft reaches to a free outfall.
junctions = """[JUNCTIONS]
;;Name           Elevation  MaxDepth   InitDepth  SurDepth   Aponded
;;-------------- ---------- ---------- ---------- ---------- ----------
JN_Toe           438.5      15.0       0.0        0.0        0.0
JN_2             437.0      15.0       0.0        0.0        0.0
JN_3             435.5      15.0       0.0        0.0        0.0
"""

outfalls = """[OUTFALLS]
;;Name           Elevation  Type       Stage Data       Gated    Route To
;;-------------- ---------- ---------- ---------------- -------- ----------
OUT_1            434.0      FREE                        NO
"""

conduits = """[CONDUITS]
;;Name           From Node        To Node          Length     Roughness  InOffset   OutOffset  InitFlow   MaxFlow
;;-------------- ---------------- ---------------- ---------- ---------- ---------- ---------- ---------- ----------
C1               JN_Toe           JN_2             500        0.035      0          0          0          0
C2               JN_2             JN_3             500        0.035      0          0          0          0
C3               JN_3             OUT_1            500        0.035      0          0          0          0
"""

xsections = """[XSECTIONS]
;;Link           Shape        Geom1      Geom2      Geom3      Geom4      Barrels
;;-------------- ------------ ---------- ---------- ---------- ---------- ----------
C1               TRAPEZOIDAL  15.0       40.0       2.0        2.0        1
C2               TRAPEZOIDAL  15.0       40.0       2.0        2.0        1
C3               TRAPEZOIDAL  15.0       40.0       2.0        2.0        1
"""

coordinates = """[COORDINATES]
;;Node           X-Coord            Y-Coord
;;-------------- ------------------ ------------------
JN_Toe           0.000              0.000
JN_2             500.000            0.000
JN_3             1000.000           0.000
OUT_1            1500.000           0.000
"""

options = f"""[TITLE]
Anson County WTP Lower Lagoon (ANSON-057) -- piping breach at normal pool.
Froehlich (2008) breach routed level-pool by swmm-breach, applied as INFLOWS
at the dam toe (JN_Toe) and conveyed down a trapezoidal channel to a free
outfall. Peak breach outflow ~{peak_cfs:,.0f} cfs (HEC-RAS 6.6 2D: 4,301 cfs).
Units: CFS / feet (NAVD88).

[OPTIONS]
FLOW_UNITS           CFS
INFILTRATION         HORTON
FLOW_ROUTING         DYNWAVE
LINK_OFFSETS         DEPTH
MIN_SLOPE            0
ALLOW_PONDING        NO
SKIP_STEADY_STATE    NO

START_DATE           06/05/2026
START_TIME           14:00:00
REPORT_START_DATE    06/05/2026
REPORT_START_TIME    14:00:00
END_DATE             06/05/2026
END_TIME             16:00:00
SWEEP_START          01/01
SWEEP_END            12/31
DRY_DAYS             0
REPORT_STEP          00:00:10
WET_STEP             00:00:10
DRY_STEP             00:05:00
ROUTING_STEP         0:00:02
RULE_STEP            00:00:00

INERTIAL_DAMPING     PARTIAL
NORMAL_FLOW_LIMITED  BOTH
FORCE_MAIN_EQUATION  H-W
VARIABLE_STEP        0.75
LENGTHENING_STEP     0
MIN_SURFAREA         12.566
MAX_TRIALS           8
HEAD_TOLERANCE       0.005
SYS_FLOW_TOL         5
LAT_FLOW_TOL         5

[EVAPORATION]
CONSTANT         0.0
DRY_ONLY         NO

[REPORT]
INPUT      NO
CONTROLS   NO
SUBCATCHMENTS ALL
NODES ALL
LINKS ALL
"""

report_map = """[MAP]
DIMENSIONS -200.000 -200.000 1700.000 200.000
Units      Feet
"""

doc = (
    options
    + "\n"
    + junctions
    + "\n"
    + outfalls
    + "\n"
    + conduits
    + "\n"
    + xsections
    + "\n"
    + inflow_block
    + "\n"
    + coordinates
    + "\n"
    + report_map
)

OUT_INP.write_text(doc, encoding="ascii")
print(f"\nWrote {OUT_INP}")
print(f"  ({len(doc.splitlines())} lines)")
