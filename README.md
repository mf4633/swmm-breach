# swmm-breach

Dam breach hydrograph generator for EPA SWMM and PCSWMM users.

`swmm-breach` predicts embankment-dam breach geometry from published
empirical regressions (Froehlich 2008) and routes the breach through a
reservoir storage curve to produce an outflow hydrograph that can be fed
back into SWMM as an `INFLOWS` time series.

## Status

Alpha (0.1.0). Implemented:

- Froehlich (2008) breach parameter regressions (`B_avg`, `t_f`) for
  piping and overtopping failure modes
- Trapezoidal-breach broad-crested-weir outflow
- Level-pool reservoir routing with linear breach growth

Planned:

- Xu-Zhang (2009), MacDonald-Langridge (1984), and NWS BREACH parameter sets
- SWMM `.inp` storage-node parser and `INFLOWS` time-series writer
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
