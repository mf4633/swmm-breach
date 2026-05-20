# Install

## Requirements

- Python ≥ 3.9
- NumPy ≥ 1.20 (runtime)
- Matplotlib ≥ 3.5 (optional, for plotting)
- pytest ≥ 7 (optional, for the test suite)

`swmm-breach` is dependency-light by design: NumPy is the only required
runtime dependency. All SWMM I/O is implemented from the documented
format specification rather than wrapping `pyswmm` or `swmm-toolkit`.

## From PyPI

Not yet on PyPI as of v0.7.0. Install from the source repository:

## From source

```bash
git clone https://github.com/mf4633/swmm-breach.git
cd swmm-breach
pip install -e .
```

### With plotting helpers

```bash
pip install -e ".[viz]"
```

This adds Matplotlib and enables [`Hydrograph.plot()`][swmm_breach.hydrograph.Hydrograph.plot]
and
[`EnsembleHydrograph.plot_envelope()`][swmm_breach.uncertainty.EnsembleHydrograph.plot_envelope].

### With the test suite

```bash
pip install -e ".[test]"
pytest
```

### With documentation tooling

```bash
pip install -e ".[docs]"
mkdocs serve
```

## Verifying the install

```python
import swmm_breach
print(swmm_breach.__version__)  # 0.7.0
```

A simple end-to-end smoke check:

```python
import numpy as np
from swmm_breach import FailureMode, StorageCurve, froehlich, simulate

storage = StorageCurve(
    stage_m=np.array([0., 5., 10.]),
    volume_m3=np.array([0., 1e5, 5e5]),
)
geom = froehlich.predict(5e5, 10., 10., FailureMode.PIPING)
hg = simulate(geom, storage, 10., 10., dt_s=10., duration_s=3600.)
print(f"Peak: {hg.peak_outflow_m3s:.1f} m^3/s")
```
