# User guide

This page walks through the full workflow that `swmm-breach` is built
around: read a SWMM `.inp`, predict the breach, route a probabilistic
ensemble, paste the result back into the SWMM model, and post-process
the downstream response.

## The workflow

```
SWMM .inp -> storage node -> breach parameters -> hydrograph ensemble
   |                                                       |
   |                                                       v
   |                              [TIMESERIES] + [INFLOWS] snippet
   |                                                       |
   v                                                       v
[run SWMM with the new boundary]                  paste into .inp
   |
   v
SWMM .out -> node depths/flows downstream
```

## 1. Reading the storage node from a SWMM .inp

```python
from swmm_breach.swmm import load_storage_curve

sc, node = load_storage_curve("project.inp", "Reservoir1")

print(f"Invert: {node.invert_elevation:.2f} m")
print(f"Max depth: {node.max_depth:.2f} m")
print(f"Volume at crest: {sc.volume_at(node.invert_elevation + node.max_depth):,.0f} m^3")
```

Only `SHAPE = TABULAR` storage is supported in v0.7. Functional shapes
raise an explicit `NotImplementedError` so input mistakes fail loudly.

## 2. Predicting the breach geometry

Two regressions are available:

```python
from swmm_breach import FailureMode, froehlich, froehlich_1995

# Froehlich 2008 (default, fit to 74 cases)
geom_2008 = froehlich.predict(
    volume_m3=sc.volume_at(node.invert_elevation + node.max_depth),
    height_m=node.max_depth,
    crest_elevation_m=node.invert_elevation + node.max_depth,
    mode=FailureMode.PIPING,
)

# Froehlich 1995 (predecessor, fit to 63 cases, different exponents)
geom_1995 = froehlich_1995.predict(
    volume_m3=sc.volume_at(node.invert_elevation + node.max_depth),
    height_m=node.max_depth,
    crest_elevation_m=node.invert_elevation + node.max_depth,
    mode=FailureMode.PIPING,
)

print(f"2008: B_avg={geom_2008.bottom_width_m:.1f}m  t_f={geom_2008.formation_time_s/60:.1f}min")
print(f"1995: B_avg={geom_1995.bottom_width_m:.1f}m  t_f={geom_1995.formation_time_s/60:.1f}min")
```

See [Theory](theory.md) for the regression equations.

## 3. Routing the breach (deterministic)

```python
from swmm_breach import simulate

hg = simulate(
    geometry=geom_2008,
    storage=sc,
    crest_elevation_m=node.invert_elevation + node.max_depth,
    initial_stage_m=node.invert_elevation + node.max_depth,
    dt_s=10.0,
    duration_s=4 * 3600,
)
print(f"Peak: {hg.peak_outflow_m3s:.0f} m^3/s at {hg.time_to_peak_s/60:.1f} min")
```

This is a single-realization deterministic routing. For real engineering
practice, use the probabilistic ensemble below.

## 4. Probabilistic ensemble (recommended)

The single-realization point estimate misses observed peaks by 80% at
large-dam scale ([Teton tutorial](tutorials/teton.md)). The probabilistic
multi-model ensemble brackets observed peaks across all scales:

```python
from swmm_breach.uncertainty import ensemble_simulate_multi_model
import numpy as np

ens = ensemble_simulate_multi_model(
    storage=sc,
    crest_elevation_m=node.invert_elevation + node.max_depth,
    initial_stage_m=node.invert_elevation + node.max_depth,
    volume_m3=sc.volume_at(node.invert_elevation + node.max_depth),
    height_m=node.max_depth,
    mode=FailureMode.PIPING,
    n_samples=2000,
    dt_s=10.0,
    duration_s=4 * 3600,
    rng=np.random.default_rng(20260511),
)

print(f"Peak Q 5/50/95: "
      f"{ens.peak_percentile(5):,.0f} / "
      f"{ens.peak_percentile(50):,.0f} / "
      f"{ens.peak_percentile(95):,.0f} m^3/s")
```

By default the ensemble samples 50/50 between Froehlich (2008) and
Froehlich (1995). Custom model mixtures are supported via the
`BreachModel` interface.

## 5. Plotting the ensemble

Requires the `viz` extra:

```python
import matplotlib.pyplot as plt
ax = ens.plot_envelope(show_realizations=True, n_realizations=20)
plt.show()
```

## 6. Pasting the result back into SWMM

```python
from datetime import datetime
from swmm_breach.swmm import format_inflows_block

# Use a single representative realization (e.g., the median peak) OR
# emit three time-series (low/median/high) for sensitivity analysis.
# Here we use the deterministic median for brevity:
block = format_inflows_block(
    hg,
    node_name="DownstreamOutfall",
    timeseries_name="TS_Breach",
    start_datetime=datetime(2026, 6, 5, 14, 0),
    units="CMS",  # or "CFS" if the project's FLOW_UNITS is CFS
    decimate=6,    # write every minute when dt_s = 10 s
)
print(block)  # paste this into project.inp, then re-run SWMM
```

## 7. Reading downstream response from the binary .out

After SWMM finishes, the binary output file contains depths and flows
at every node and link:

```python
from swmm_breach.output import node_series, link_series, NodeVariable, LinkVariable

t, depth = node_series("project.out", "DownstreamJN", NodeVariable.DEPTH)
_, flow = link_series("project.out", "Pipe1", LinkVariable.FLOW)

print(f"Max downstream depth: {depth.max():.2f} m at t={t[depth.argmax()]/60:.1f} min")
```

## Common pitfalls

- **Unit mismatch.** `swmm-breach` is internally SI (m, m³, m³/s). If your
  SWMM project uses CFS, pass `units="CFS"` to
  [`format_inflows_block`][swmm_breach.swmm.format_inflows_block] to
  convert at the boundary.
- **Functional storage shapes.** Only TABULAR storage works in v0.7.
- **Linear breach growth assumption.** The package assumes the breach
  grows linearly from zero width over the formation time. This
  approximation breaks down at large-dam scales where headcut migration
  dominates; the deterministic point estimate over-predicts peaks at
  Teton scale by approximately 80% for this reason. The probabilistic
  envelope is the recommended representation; see the [Teton tutorial](tutorials/teton.md).
