# Contributing to swmm-breach

Thanks for your interest in contributing! `swmm-breach` is a small,
focused package and the contribution model is informal. If you're
unsure whether a change fits the package's scope, open an issue first
to discuss before writing code.

## Reporting bugs

Open an issue at <https://github.com/mf4633/swmm-breach/issues> with:

- `swmm-breach` version (`pip show swmm-breach` or `python -c "import swmm_breach; print(swmm_breach.__version__)"`)
- Python version and operating system
- A minimal example that reproduces the bug
- Expected behaviour vs. what you actually observed

## Suggesting features

Open an issue with the `enhancement` label and describe the use case.
Features that fit the package's scope — probabilistic embankment-dam
breach hydrograph forecasting and SWMM input/output integration —
will generally be welcomed. Out-of-scope examples include real-time
streaming, 2D inundation modelling, and structural breach mechanics.

## Pull requests

1. Fork the repo and create a feature branch off `main`
2. Install with dev dependencies:
   ```bash
   pip install -e ".[test,viz,docs]"
   ```
3. Make your change with accompanying tests in `tests/`
4. Run the full suite:
   ```bash
   pytest
   ```
5. If you change public API, update the affected docstrings and the
   relevant page in `docs/`. Run `mkdocs serve` to verify the docs
   build locally.
6. Open a PR against `main` describing what changed and why; reference
   the issue you're fixing if applicable.

## Adding a new breach regression

The `BreachModel` interface in `swmm_breach.uncertainty` accepts any
breach regression conforming to:

```python
b_avg_fn(volume_m3, height_m, mode) -> float        # average bottom width, metres
t_f_fn(volume_m3, height_m, mode) -> float          # formation time, seconds
side_slope_fn(mode) -> float                        # H per V
```

plus log-residual sigmas `sigma_log_b_avg` and `sigma_log_t_f`.

New regressions should be implemented in their own module under `src/swmm_breach/`
(e.g., `xu_zhang.py`, `nws_breach.py`) and added to `default_models()`
in `swmm_breach.uncertainty` only after validation against at least one
historical case in the package's test suite.

## Adding a new validation case

Validation cases live in `tests/test_<case>.py` and ideally have a
companion runnable script in `examples/`. A new case should:

1. Use parameters from a citable public source (a USGS report, the Wahl
   2004 database, a published HEC-RAS reference run, an open NCDS / state
   dam-safety record)
2. Document the source clearly in the test docstring
3. Add a regression assertion that the multi-model ensemble brackets
   the reference peak
4. Optionally add a tutorial page under `docs/tutorials/` with rendered
   figure

## Code style

- Black-compatible formatting (line length 88)
- Type hints on public functions where reasonable
- NumPy-style docstrings (mkdocstrings is configured to render them)
- pytest tests; no test framework dependencies beyond pytest

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By
participating, you agree to uphold it. Report unacceptable behaviour to
michaelbflynn@gmail.com.
