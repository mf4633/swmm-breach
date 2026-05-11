"""End-to-end smoke run: Teton fixture .inp -> breach -> SWMM inflow block."""

from datetime import datetime

from swmm_breach import FailureMode, froehlich, simulate
from swmm_breach.swmm import format_inflows_block, load_storage_curve

INP = "tests/data/teton_minimal.inp"

sc, node = load_storage_curve(INP, "TetonRes")
crest = node.invert_elevation + node.max_depth

print("=== Storage node from .inp ===")
print(f"  name           : {node.name}")
print(f"  invert elev    : {node.invert_elevation:.1f} m")
print(f"  max depth      : {node.max_depth:.1f} m")
print(f"  crest elev     : {crest:.1f} m")
print(f"  vol at crest   : {sc.volume_at(crest):,.0f} m^3")
print()

geom = froehlich.predict(
    volume_m3=sc.volume_at(crest),
    height_m=node.max_depth,
    crest_elevation_m=crest,
    mode=FailureMode.PIPING,
)
print("=== Froehlich (2008) breach geometry ===")
print(f"  B_avg          : {geom.bottom_width_m:.1f} m   (Teton observed 151)")
print(f"  t_f            : {geom.formation_time_s/60:.1f} min   (observed 75)")
print(f"  side slope H:V : {geom.side_slope_h_per_v}")
print(f"  invert elev    : {geom.invert_elevation_m:.1f} m")
print()

hg = simulate(
    geometry=geom,
    storage=sc,
    crest_elevation_m=crest,
    initial_stage_m=crest,
    dt_s=10.0,
    duration_s=4 * 3600,
)
print("=== Routed hydrograph ===")
print(f"  peak outflow   : {hg.peak_outflow_m3s:,.0f} m^3/s")
print(f"  time to peak   : {hg.time_to_peak_s/60:.1f} min")
print(f"  final stage    : {hg.stage_m[-1]:.1f} m   (started at {hg.stage_m[0]:.1f})")
print(f"  final volume   : {sc.volume_at(hg.stage_m[-1]):,.0f} m^3")
print()

block = format_inflows_block(
    hg,
    node_name="DownstreamOutfall",
    timeseries_name="TS_TetonBreach",
    start_datetime=datetime(2026, 6, 5, 14, 0, 0),
    units="CMS",
    decimate=30,  # write every 5 minutes when dt_s = 10 s
)
print("=== SWMM .inp snippet (truncated) ===")
lines = block.splitlines()
for line in lines[:18]:
    print("  " + line)
print(f"  ... ({len(lines)} total lines)")
print()
print(f"  ...{lines[-5]}")
print(f"  {lines[-4]}")
print(f"  {lines[-3]}")
print(f"  {lines[-2]}")
