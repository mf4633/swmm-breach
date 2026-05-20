# swmm-breach

**Probabilistic dam-breach hydrograph forecasting for EPA SWMM and PCSWMM.**

`swmm-breach` is a small, MIT-licensed Python package that adds dam-breach
hydrograph generation to EPA SWMM and PCSWMM models. It implements the
Froehlich (1995, 2008) breach parameter regressions, Wahl (2004)-style
Monte Carlo uncertainty propagation, multi-model ensemble averaging, and
end-to-end `.inp` / `.out` integration.

## Why this exists

EPA SWMM is one of the most widely deployed open-source urban-hydrology
engines in the world, but it has no native facility for simulating
embankment-dam, detention-basin, or sediment-lagoon failure.
Practitioners working on dam-adjacent SWMM models currently either bounce
out to HEC-RAS (losing the SWMM network model) or hand-construct the
breach boundary in spreadsheets.

Meanwhile, Wahl (2004) showed two decades ago that the dominant breach
parameter regressions carry factor-of-2 to factor-of-10 uncertainty on
peak discharge, and recommended Monte Carlo simulation as the
appropriate response. Most engineering practice still reports a single
deterministic peak.

`swmm-breach` closes both gaps in one ~1,500-LOC Python package.

## At a glance

```python
import numpy as np
from swmm_breach import FailureMode, StorageCurve
from swmm_breach.uncertainty import ensemble_simulate_multi_model

storage = StorageCurve(
    stage_m=np.array([0, 20, 40, 60, 80, 87]),
    volume_m3=np.array([0, 12e6, 60e6, 160e6, 290e6, 308e6]),
)

ens = ensemble_simulate_multi_model(
    storage=storage,
    crest_elevation_m=87.0,
    initial_stage_m=87.0,
    volume_m3=308e6,
    height_m=86.9,
    mode=FailureMode.PIPING,
    n_samples=2000,
)
print(f"Peak Q 5/50/95: {ens.peak_percentile(5):,.0f} / "
      f"{ens.peak_percentile(50):,.0f} / "
      f"{ens.peak_percentile(95):,.0f} m^3/s")
```

## Validation

Three reference cases spanning four orders of magnitude in reservoir
volume; the probabilistic 5-95 envelope brackets the reference peak in
every case.

| Case | Volume (m³) | Reference peak | Source | In envelope |
|---|---:|---:|---|:---:|
| [Anson Lower Lagoon (2026)](tutorials/anson.md) | 7.9 × 10⁴ | 122 m³/s | HEC-RAS 6.6 2D | yes |
| [Lawn Lake Dam (1982)](tutorials/lawn-lake.md) | 8.0 × 10⁵ | 510 m³/s | Jarrett & Costa USGS | yes |
| [Teton Dam (1976)](tutorials/teton.md) | 3.1 × 10⁸ | 50,000-80,000 m³/s | Wahl (2004) | yes |

## Next steps

- [Install](install.md) the package
- Work through a [tutorial](tutorials/index.md)
- Read the [user guide](user-guide.md) or [theory](theory.md)
- Browse the [API reference](api.md)
- See the [changelog](changelog.md) for release history
