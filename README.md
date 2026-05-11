# swmm-breach

Dam breach hydrograph generator for EPA SWMM and PCSWMM users.

`swmm-breach` predicts embankment-dam breach geometry from published
empirical regressions (Froehlich 2008) and routes the breach through a
reservoir storage curve to produce an outflow hydrograph that can be fed
back into SWMM as an `INFLOWS` time series.

## Status

Alpha (0.3.0). Implemented:

- Froehlich (2008) breach parameter regressions (`B_avg`, `t_f`) for
  piping and overtopping failure modes
- Trapezoidal-breach broad-crested-weir outflow
- Level-pool reservoir routing with linear breach growth
- SWMM 5.x `.inp` integration (pre-processing): parse `[STORAGE]`
  (TABULAR) + `[CURVES]`, emit pasteable `[TIMESERIES]` + `[INFLOWS]`
  blocks with CFS/CMS conversion
- SWMM 5.x `.out` integration (post-processing): read header, node and
  link time series for the standard reporting variables

> **Note:** the `.out` reader has been round-tripped against synthetic
> fixtures generated to the documented SWMM 5 format spec. Validation
> against an actual SWMM-engine-produced `.out` is pending.

Planned:

- Xu-Zhang (2009), MacDonald-Langridge (1984), and NWS BREACH parameter sets
- Functional storage shapes; pyswmm/swmm-toolkit interop
- Muskingum routing for downstream channel attenuation
- Inundation envelope (normal-depth or simplified 2D)

## Install

```bash
pip install swmm-breach          # from PyPI (when published)
pip install -e ".[test]"          # from source, with test deps
```

Requires Python >= 3.9 and NumPy.

## Quick start

```python
import numpy as np
from swmm_breach import FailureMode, StorageCurve, froehlich, simulate

storage = StorageCurve(
    stage_m=np.array([0, 20, 40, 60, 80, 87]),
    volume_m3=np.array([0, 12e6, 60e6, 160e6, 290e6, 308e6]),
)

geom = froehlich.predict(
    volume_m3=308e6,
    height_m=86.9,
    crest_elevation_m=87.0,
    mode=FailureMode.PIPING,
)

hg = simulate(
    geometry=geom,
    storage=storage,
    crest_elevation_m=87.0,
    initial_stage_m=87.0,
    dt_s=10.0,
    duration_s=8 * 3600,
)

print(f"Peak outflow:  {hg.peak_outflow_m3s:,.0f} m^3/s")
print(f"Time to peak:  {hg.time_to_peak_s/60:.1f} min")
```

## SWMM round-trip

```python
from datetime import datetime
from swmm_breach import FailureMode, froehlich, simulate
from swmm_breach.swmm import load_storage_curve, format_inflows_block

# 1. Pull a storage curve straight out of an existing .inp
sc, node = load_storage_curve("model.inp", "TetonRes")
crest = node.invert_elevation + node.max_depth

# 2. Predict breach geometry and route the breach
geom = froehlich.predict(
    volume_m3=sc.volume_at(crest),
    height_m=node.max_depth,
    crest_elevation_m=crest,
    mode=FailureMode.PIPING,
)
hg = simulate(geom, sc, crest, initial_stage_m=crest, dt_s=10.0,
              duration_s=4*3600)

# 3. Emit a SWMM-pasteable inflow block for the downstream node
print(format_inflows_block(
    hg, node_name="DownstreamOutfall",
    timeseries_name="TS_TetonBreach",
    start_datetime=datetime(2026, 6, 5, 14, 0),
    units="CMS",  # or "CFS" if FLOW_UNITS in [OPTIONS] is CFS
    decimate=6,    # write every minute when dt_s=10
))
```

Paste the printed snippet into the project's `.inp` and re-run SWMM.

## Reading SWMM `.out` results

After re-running SWMM with the breach inflow, pull the downstream
response back out for inundation reporting:

```python
from swmm_breach.output import NodeVariable, LinkVariable, node_series, link_series

t, depth = node_series("model.out", "DownstreamJN", NodeVariable.DEPTH)
_, head  = node_series("model.out", "DownstreamJN", NodeVariable.HEAD)
_, flow  = link_series("model.out", "Outfall_Pipe", LinkVariable.FLOW)

print(f"Max downstream depth: {depth.max():.2f} m at t = {t[depth.argmax()]/60:.1f} min")
```

## Validation

The Froehlich (2008) regressions reproduce the observed Teton Dam (1976)
breach geometry to within the typical 25 % accuracy of empirical breach
formulas:

| Parameter            | Observed | Predicted |
|----------------------|---------:|----------:|
| Average bottom width |    151 m |    ~168 m |
| Formation time       |  1.25 hr |   ~1.13 hr |

See `tests/test_froehlich.py` for the assertions, and
`tests/test_hydrograph.py` for the end-to-end routing test.

## References

- Froehlich, D. C. (2008). "Embankment Dam Breach Parameters and Their
  Uncertainties." *Journal of Hydraulic Engineering* 134(12), 1708-1721.
- Wahl, T. L. (2004). "Uncertainty of Predictions of Embankment Dam
  Breach Parameters." *Journal of Hydraulic Engineering* 130(5), 389-397.

## License

MIT
