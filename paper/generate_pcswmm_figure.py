"""Generate the JWMM applied-case figure from the Anson PCSWMM run.

Reads the EPA SWMM 5.2.4 ``.out`` produced by routing
``examples/anson_pcswmm_example.inp`` and plots the breach inflow at the
dam toe against the downstream flow-depth response -- the inundation-
relevant view of the routed breach. If the ``.out`` is absent it is
regenerated with the EPA SWMM CLI (``runswmm.exe``); failing that, the
script falls back to plotting the swmm-breach hydrograph alone.

Output meets JWMM figure specs: vector PDF, serif (Times) font, no bold,
black-and-white-safe (solid vs dashed, no color-only encoding),
landscape within 7.0 x 4.25 in. A 300-dpi PNG preview is also written.

    .venv\\Scripts\\python.exe paper\\generate_pcswmm_figure.py
"""

import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from swmm_breach.output import NodeVariable, node_series, read_metadata

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
INP = REPO / "examples" / "anson_pcswmm_example.inp"
OUT = REPO / "examples" / "anson_pcswmm_example.out"
RPT = REPO / "examples" / "anson_pcswmm_example.rpt"
PDF = HERE / "anson_routing.pdf"
PNG = HERE / "anson_routing.png"

CFS_PER_CMS = 35.31466621266132
FT_PER_M = 1.0 / 0.3048
HEC_RAS_PEAK_CFS = 4301.0

# JWMM-compliant styling: serif, no bold, modest sizes.
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size": 10,
    "axes.titlesize": 10,
    "axes.labelsize": 10,
    "legend.fontsize": 9,
    "axes.linewidth": 0.8,
    "figure.dpi": 300,
})


def ensure_out() -> bool:
    if OUT.exists():
        return True
    runswmm = Path(r"C:\Program Files (x86)\EPA SWMM 5.2.4\runswmm.exe")
    if INP.exists() and runswmm.exists():
        subprocess.run([str(runswmm), str(INP), str(RPT), str(OUT)], check=True)
        return OUT.exists()
    return False


def main() -> None:
    if not ensure_out():
        raise SystemExit("Anson .out not found and could not be generated.")

    meta = read_metadata(OUT)
    assert meta.flow_units == "CFS"  # Anson model is US-customary

    # Discharge is stored in cfs; depth (CFS units) in feet. Plot SI-primary.
    t_s, inflow_cfs = node_series(OUT, "JN_Toe", NodeVariable.TOTAL_INFLOW)
    _, depth_ft = node_series(OUT, "JN_3", NodeVariable.DEPTH)
    t_min = t_s / 60.0
    inflow_cms = inflow_cfs / CFS_PER_CMS
    depth_m = depth_ft / FT_PER_M

    fig, ax_q = plt.subplots(figsize=(7.0, 4.0))

    # Breach inflow (left axis) -- solid.
    l1, = ax_q.plot(t_min, inflow_cms, color="black", linewidth=1.6,
                    linestyle="-", label="breach inflow at dam toe")
    # HEC-RAS 2D reference peak -- dotted horizontal.
    ax_q.axhline(HEC_RAS_PEAK_CFS / CFS_PER_CMS, color="0.45", linewidth=1.0,
                 linestyle=":", label="HEC-RAS 6.6 2D peak (4,301 cfs)")
    ax_q.set_xlabel("time since breach initiation (min)")
    ax_q.set_ylabel(r"discharge (m$^3$/s)")
    ax_q.set_xlim(0, 60)
    ax_q.set_ylim(bottom=0)

    # cfs companion axis (US customary in parentheses, per JWMM units rule).
    ax_cfs = ax_q.twinx()
    ax_cfs.set_ylabel("discharge (cfs)")
    ax_cfs.set_ylim(ax_q.get_ylim()[0] * CFS_PER_CMS,
                    ax_q.get_ylim()[1] * CFS_PER_CMS)

    # Downstream flow depth -- separate panel-style axis via a second figure
    # axis would crowd; instead overlay depth on a third spine offset right.
    ax_d = ax_q.twinx()
    ax_d.spines["right"].set_position(("axes", 1.12))
    l2, = ax_d.plot(t_min, depth_m, color="black", linewidth=1.4,
                    linestyle="--", label="downstream flow depth (JN_3)")
    ax_d.set_ylabel("flow depth (m)")
    ax_d.set_ylim(bottom=0)

    lines = [l1, l2, ax_q.lines[1]]
    ax_q.legend(lines, [ln.get_label() for ln in lines],
                loc="upper right", frameon=False)
    ax_q.grid(True, which="major", axis="both", color="0.85", linewidth=0.5)

    fig.tight_layout()
    fig.savefig(PDF)
    fig.savefig(PNG, dpi=300)
    print(f"Peak breach inflow : {inflow_cms.max():.1f} m^3/s "
          f"({inflow_cfs.max():.0f} cfs)")
    print(f"Peak downstream depth: {depth_m.max():.2f} m ({depth_ft.max():.1f} ft)")
    print(f"Wrote {PDF}")
    print(f"Wrote {PNG}")


if __name__ == "__main__":
    main()
