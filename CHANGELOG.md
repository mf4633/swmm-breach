# Changelog

All notable changes to `swmm-breach` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- MkDocs Material documentation site at `https://mf4633.github.io/swmm-breach/`
- `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
- Per-tutorial ensemble envelope figures (Anson, Lawn Lake, Teton)
- Runnable EPA SWMM/PCSWMM example models in `examples/` (`teton_pcswmm_example.inp`, CMS/m; `anson_pcswmm_example.inp`, CFS/ft) plus the generators that build them; both verified clean in EPA SWMM 5.2.4 and PCSWMM Professional 2D
- `.out` reader validated against real EPA SWMM 5.2.4 engine output (`tests/test_output_real_engine.py` + `tests/data/teton_real_engine.out`), removing the prior synthetic-fixture-only caveat
- Consolidated the manuscript onto a single target venue — JWMM (`paper/jwmm/`); removed the EMS, SoftwareX, and JOSS drafts and the JOSS `paper.yml` workflow

## [0.7.0] - 2026-05-11

### Added
- `Hydrograph.plot()` returns a matplotlib `Axes` for a single-realization hydrograph
- `EnsembleHydrograph.plot_envelope()` plots median + 5-95 percentile band, with optional individual-realization overlay
- `[viz]` optional install extra (`pip install swmm-breach[viz]`) adds Matplotlib for plotting helpers
- `paper/generate_figures.py` for reproducible JOSS paper figures
- `paper/teton_ensemble.png` embedded in the JOSS paper as Figure 1
- `.github/workflows/paper.yml` compiles the JOSS paper PDF on every change to `paper/`

### Changed
- Validation table in `paper/paper.md` updated to use multi-model ensemble numbers consistently (was inconsistently mixing single-model and multi-model)
- Bumped to v0.7.0

## [0.6.0] - 2026-05-11

### Added
- `swmm_breach.froehlich_1995` module: Froehlich (1995) breach parameter regressions (predecessor to Froehlich 2008, different exponents, smaller fitted database)
- `BreachModel` dataclass + `ensemble_simulate_multi_model` function in `swmm_breach.uncertainty` for multi-model Monte Carlo sampling
- `default_models()` returns the two-model Froehlich 2008 + 1995 ensemble (equal weight)
- Lawn Lake Dam (1982) third validation case (`tests/test_lawn_lake_case.py`, `examples/lawn_lake_1982.py`)
- GitHub Actions CI matrix on Linux/macOS/Windows × Python 3.9-3.12 (12 jobs per push)
- README CI badge, MIT license badge, Python 3.9+ badge

### Changed
- Bumped to v0.6.0; tagged release on GitHub

## [0.5.0] - 2026-05-11

### Added
- Anson County WTP Lower Lagoon (ANSON-057) second validation case study
- `examples/anson_lower_lagoon.py` runnable script
- `tests/test_anson_case.py` regression tests (HEC-RAS 6.6 2D unsteady reference: 4,301 cfs / 121.8 m³/s)
- Anson Validation §2 in `paper/paper.md`; comparison table across all cases

### Changed
- Paper Validation section restructured as multi-case story spanning ~4 orders of magnitude in reservoir volume

## [0.4.0] - 2026-05-11

### Added
- `swmm_breach.uncertainty` module: Wahl (2004)-style Monte Carlo uncertainty propagation
- `FroehlichUncertainty` dataclass with default log-residual sigmas (σ_log B_avg=0.110, σ_log t_f=0.197)
- `sample_breach_parameters()` draws log-normal residual samples
- `ensemble_simulate()` routes the full ensemble through level-pool dynamics
- `EnsembleHydrograph` with per-time-step percentile envelopes and per-realization peak distribution
- Teton bracketing validation test in `tests/test_uncertainty.py`
- `paper/paper.md` JOSS submission draft and `paper/paper.bib`

## [0.3.0] - 2026-05-11

### Added
- `swmm_breach.output` SWMM 5 `.out` binary file reader (post-processing)
- `read_metadata`, `node_series`, `link_series` functions
- `NodeVariable` and `LinkVariable` IntEnums (DEPTH/HEAD/VOLUME/INFLOW/FLOW/etc.)
- Closing-block-first parse strategy: jump to section offsets rather than walking through input properties
- 9 round-trip tests using synthetic fixtures generated independently from the EPA SWMM `output.c` format spec
- README section on reading `.out` files

## [0.2.0] - 2026-05-11

### Added
- `swmm_breach.swmm` SWMM `.inp` integration (pre-processing)
- `read_sections`, `parse_storage_nodes`, `parse_curves`, `load_storage_curve`
- `format_inflows_block()` emits paste-ready `[TIMESERIES]` + `[INFLOWS]` snippet for SWMM `.inp` files
- Automatic CFS ↔ CMS unit conversion (factor 35.31466621266132)
- TABULAR storage shapes supported; FUNCTIONAL shapes raise `NotImplementedError`
- No `pyswmm` / `swmm-toolkit` dependency; thin parser keeps install footprint to NumPy alone

## [0.1.0] - 2026-05-11

### Added
- Initial scaffold
- `swmm_breach.froehlich` module with Froehlich (2008) regressions: `average_breach_width`, `formation_time`, `side_slope`, `predict`
- `swmm_breach.breach` module: `BreachGeometry` dataclass, `FailureMode` enum
- `swmm_breach.reservoir` module: `StorageCurve`, `trapezoidal_breach_outflow`
- `swmm_breach.hydrograph` module: `simulate()` linear-growth breach + level-pool routing through a developing trapezoidal broad-crested-weir
- MIT license, src/ layout, hatchling build backend, Python ≥ 3.9, NumPy ≥ 1.20
- 12 passing tests including Teton Dam (1976) validation (B_avg and t_f within 25 % of observed)
