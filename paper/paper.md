---
title: 'swmm-breach: Probabilistic dam-breach hydrograph forecasting for EPA SWMM and PCSWMM'
tags:
  - Python
  - hydrology
  - dam safety
  - SWMM
  - flood modeling
  - uncertainty quantification
authors:
  - name: Michael B. Flynn
    orcid: 0009-0004-2410-7950
    affiliation: 1
affiliations:
  - name: Independent researcher, Asheville, NC, USA
    index: 1
date: 11 May 2026
bibliography: paper.bib
---

# Summary

`swmm-breach` is a small, dependency-light Python package that adds
dam-breach hydrograph generation to the EPA Storm Water Management
Model (SWMM) [@rossman2017] and its commercial extension PCSWMM. SWMM
is one of the most widely deployed open-source urban-hydrology engines
worldwide, but it has no native capability to simulate the failure of
an embankment dam, detention basin, levee, or sediment pond stored as
a `STORAGE` node. Practitioners working on dam-adjacent SWMM models
currently either bounce out to the U.S. Army Corps' HEC-RAS for the
breach hydrograph — losing the SWMM network model in the process — or
hand-construct the boundary condition in spreadsheets and manually
paste a `[TIMESERIES]` block into the `.inp` file.

`swmm-breach` closes this gap with a single Python API that:

1. Reads a SWMM `.inp` file and extracts the storage curve and
   geometry of a named storage node;
2. Predicts breach geometry (average bottom width and formation time)
   using the @froehlich2008 or @froehlich1995 regressions for piping
   and overtopping failure modes;
3. Routes the developing breach through a level-pool reservoir model
   with a trapezoidal broad-crested-weir outflow;
4. Quantifies prediction uncertainty by Monte Carlo sampling of the
   regressions' published log-normal residuals, after @wahl2004,
   producing ensemble hydrographs with confidence envelopes; samples
   can be drawn from a single regression or a weighted mixture of
   models, capturing both *parametric* (within-model) and *epistemic*
   (between-model) uncertainty;
5. Emits a paste-ready `[TIMESERIES]` and `[INFLOWS]` snippet for the
   downstream node, with automatic CFS/CMS unit conversion;
6. Reads the SWMM binary `.out` file after re-running the model to
   pull back simulated downstream depths and flows for inundation
   reporting.

NumPy is the only runtime dependency. The `.inp` parser and `.out`
binary reader are written from the documented EPA SWMM 5 format spec
rather than wrapping `pyswmm` or `swmm-toolkit`, keeping the install
footprint minimal and auditable for engineering practice.

# Statement of need

@wahl2004 demonstrated two decades ago that the most widely used
embankment-dam breach parameter regressions carry standard errors of
estimate on the order of 0.3-1.0 in $\log_{10}$ units, implying
factor-of-two to factor-of-ten prediction uncertainty on peak breach
discharge. He explicitly argued that "use of a single best estimate
of the breach parameters" is inadequate for dam-safety decisions and
recommended Monte Carlo simulation as the appropriate response. Yet
in the two decades since, breach analyses in engineering practice
overwhelmingly continue to report a single deterministic peak,
because no open-source tool has been available to do otherwise.

The picture in the open-source SWMM ecosystem mirrors this gap:

- HEC-RAS implements progressive breach erosion models but cannot
  ingest or emit SWMM `.inp` files, so it cannot be used inside a
  SWMM network model;
- PCSWMM offers some breach analysis through its commercial GUI, but
  the implementation is closed and the tool is not free;
- To the author's knowledge, no pip-installable Python package exists
  that combines SWMM I/O with probabilistic dam-breach forecasting.

`swmm-breach` is, to the author's knowledge, the first open-source
Python implementation of:

1. End-to-end dam-breach workflow integration with EPA SWMM and PCSWMM
   (`.inp` storage-curve extraction $\rightarrow$ breach hydrograph
   $\rightarrow$ `.out` downstream response);
2. Monte Carlo uncertainty propagation on @froehlich2008 and
   @froehlich1995 breach parameters using @wahl2004 log-normal
   residuals;
3. Multi-model ensemble averaging that samples across both parameter
   and model uncertainty, producing ensemble hydrographs and
   confidence envelopes that can be fed directly into SWMM as
   low/median/high boundary conditions.

Target users are dam-safety consulting engineers, regulatory
reviewers at state dam-safety offices, and hydrology researchers
comparing breach formulations on standard benchmark cases.

# Validation

`swmm-breach` is validated against two independent reference cases
that span almost four orders of magnitude in reservoir volume.

## Teton Dam (1976), 308,000,000 m^3

The deterministic Froehlich (2008) implementation reproduces the
canonical Teton Dam failure [@wahl2004] to within the 25 % accuracy
typical of empirical breach regressions: predicted average bottom
width 168 m vs. observed 151 m; predicted formation time 1.13 hr vs.
observed 1.25 hr.

A 2,000-realization probabilistic ensemble of the same Teton scenario
brackets the historically reported peak discharge of approximately
50,000-80,000 m$^3$/s within its 5-95 percentile envelope (5th
percentile 62,800 m$^3$/s, 95th percentile 183,000 m$^3$/s). The
deterministic point-estimate routing yields a peak of 119,000 m$^3$/s
-- approximately 80 % above the observed peak -- illustrating
concretely the @wahl2004 finding that single-value breach predictions
are systematically misleading at large reservoir scale.

## Anson County WTP Lower Lagoon (ANSON-057), 78,940 m^3

A second case study compares against an independent HEC-RAS 6.6 2D
unsteady-flow analysis performed for a Class C to Class A hazard
reclassification submittal to the North Carolina Dam Safety Program
(April 2026; the submittal and underlying as-built survey are public
records under N.C. Gen. Stat. § 132-1). The Lower Lagoon is an
HDPE-lined earthen embankment (structural height 7.62 m, normal pool
volume 78,940 m$^3$); parameters were extracted from the 2023
post-rehabilitation as-built survey.

For the Lower-piping-at-normal-pool scenario, the HEC-RAS reference
peak breach outflow is 121.8 m$^3$/s (4,301 cfs). `swmm-breach` returns:

- Deterministic point estimate: 142.5 m$^3$/s (5,034 cfs), 17 % high
- Probabilistic 5/50/95 percentiles: 77.0 / 140.5 / 219.5 m$^3$/s
  (2,719 / 4,963 / 7,753 cfs)

The HEC-RAS reference lies within the 5-95 percentile envelope; the
ensemble median is within a factor of 1.15 of HEC-RAS, well inside
the factor-of-two tolerance commonly used for breach-model agreement.

## Lawn Lake Dam (1982), 798,500 m^3

A third case fills the volume gap between Anson and Teton. The Lawn
Lake earthen embankment in Rocky Mountain National Park, Colorado
failed by piping on 15 July 1982; the failure is documented in the
public USGS report by @jarrettcosta1986 and is one of the most-cited
entries in @wahl2004's breach database (V_w = 798,500 m$^3$, h_b =
6.4 m, observed peak ~510 m$^3$/s).

A 2,000-realization multi-model ensemble (Froehlich 2008 + Froehlich
1995, equal weights) returns 5/50/95 percentile peaks of
202 / 344 / 539 m$^3$/s. The observed Jarrett & Costa peak (510 m$^3$/s)
lies inside the envelope.

## Across all three cases

| Case        | Volume (m$^3$) | Reference peak (m$^3$/s) | Ensemble 5/50/95 (m$^3$/s) | In envelope |
|-------------|---------------:|-------------------------:|----------------------------:|:-----------:|
| Anson Lower |    7.9 $\times$ 10$^4$ | 122 (HEC-RAS 2D) | 77 / 141 / 220       | yes |
| Lawn Lake   |    8.0 $\times$ 10$^5$ | 510 (Jarrett 1986) | 202 / 344 / 539    | yes |
| Teton       |    3.1 $\times$ 10$^8$ | 50,000-80,000 (observed) | 62,800 / 117,000 / 183,000 | yes |

Together the three cases demonstrate that the probabilistic ensemble
brackets the reference peak across nearly four orders of magnitude in
reservoir volume. Deterministic accuracy is scale-dependent: $\sim$17 %
deviation at lagoon scale where level-pool dynamics dominate versus
$\sim$80 % deviation at the Teton scale where headcut migration and
dynamic side-slope evolution are first-order processes that the linear-
growth model cannot resolve. All three bracketing tests are included
in the automated test suite (`tests/test_uncertainty.py`,
`tests/test_anson_case.py`, `tests/test_lawn_lake_case.py`) as
regression checks.

# Limitations

The current routing implementation uses a quasi-steady broad-crested-
weir outflow with linear breach growth; it does not resolve headcut
migration, dynamic side-slope evolution, or the transition from weir
to orifice flow that is characteristic of the late stages of an
overtopping failure. Future releases are planned to add the
@xuzhang2009 and @fread1988 (NWS BREACH) parameter sets and a
physics-based progressive-breach option.

# Acknowledgements

The author thanks the EPA SWMM development team for maintaining the
SWMM source code as open and public, which made the format-spec-
driven implementation of the `.inp` and `.out` integration possible.

# Funding and conflict of interest

No external funding was received for the development of `swmm-breach`.
The author is employed as a Professional Engineer at McGill Associates,
PA, which prepared the public-record Anson County hazard reclassification
submittal cited as a validation case in this paper. McGill Associates
had no role in the design, development, or analysis of this software;
`swmm-breach` was developed independently outside the author's
employment. The Anson submittal and its underlying parameters are
public records under N.C. Gen. Stat. § 132-1.

# References
