# swmm-breach: Probabilistic dam-breach hydrograph forecasting for EPA SWMM and PCSWMM

**Michael B. Flynn**

Independent researcher, Asheville, NC 28801, USA

ORCID: 0009-0004-2410-7950

Corresponding author: michaelbflynn@gmail.com

# Abstract

EPA SWMM and PCSWMM are among the most widely deployed open-source urban-hydrology engines, but neither provides a native facility for simulating embankment-dam or detention-basin failure. Wahl [1] showed two decades ago that empirical breach regressions carry factor-of-two to factor-of-four multiplicative uncertainty on peak discharge and recommended Monte Carlo sampling of breach-geometry parameters from log-normal distributions with the published regression standard errors of estimate. No open-source SWMM tool has implemented this. `swmm-breach` is an MIT-licensed Python package providing end-to-end probabilistic dam-breach hydrograph forecasting for EPA SWMM and PCSWMM. Across three reference cases spanning more than three orders of magnitude in reservoir volume, the 5–95 percentile envelope contains the reference peak in all three cases tested; three cases is too few to validate predictive-interval calibration in the formal sense and the reference rank within the predictive distribution is reported alongside the envelope.

# Keywords

dam safety; breach hydrology; EPA SWMM; PCSWMM; Monte Carlo uncertainty; open-source software

# Metadata

| Nr  | Code metadata description                                              | Metadata                                                                       |
|-----|------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| C1  | Current code version                                                   | v0.7.0                                                                         |
| C2  | Permanent link to code/repository used for this code version           | https://github.com/mf4633/swmm-breach                                          |
| C3  | Legal code license                                                     | MIT License                                                                    |
| C4  | Code versioning system used                                            | git                                                                            |
| C5  | Software code languages, tools and services used                       | Python; NumPy; pytest; GitHub Actions CI                                       |
| C6  | Compilation requirements, operating environments and dependencies      | Python 3.9–3.12; NumPy ≥ 1.20; optional Matplotlib ≥ 3.5; Linux/macOS/Windows  |
| C7  | If available, link to developer documentation/manual                   | https://github.com/mf4633/swmm-breach#readme                                   |
| C8  | Support email for questions                                            | michaelbflynn@gmail.com                                                        |

# 1. Motivation and significance

In the United States the National Inventory of Dams [2] catalogs more than 91,000 structures, of which approximately 15,600 are classified as high hazard — meaning that failure would likely cause loss of life downstream. The hydrograph released by a breaching embankment is the primary forcing for downstream inundation and damage analyses, and federal and state regulators are progressively requiring dam owners to characterize the full uncertainty distribution of failure consequences to support risk-informed decisions about spillway sizing, hazard reclassification, and Emergency Action Plan (EAP) inundation mapping.

Wahl [1] showed that the dominant empirical breach regressions carry standard errors of estimate on the order of 0.10–0.40 in log₁₀ units on breach-geometry parameters, with directly-fitted peak-discharge regressions reporting SEoEs of 0.32–0.59 log₁₀ units. Propagated through the broad-crested-weir relationship, the resulting multiplicative uncertainty on the predicted peak is of the order of a factor of two to four. Wahl's recommended response was Monte Carlo simulation that samples each breach-geometry parameter from a log-normal distribution centered on the regression's central estimate with standard deviation equal to the regression's published log₁₀ SEoE. We refer to this as "Wahl-style" sampling in the remainder of this paper. In the two decades since, breach analyses in engineering practice have continued to report deterministic peaks, in part because no widely available open-source tool implements Wahl's recommendation in a form practitioners can use within their existing modeling workflows.

The U.S. EPA Storm Water Management Model (SWMM) [3] and its commercial extension PCSWMM together dominate North American consulting practice for urban stormwater, combined-sewer, and small-watershed hydraulic analyses. SWMM's `STORAGE` node primitive can represent ponds, detention basins, sediment lagoons, and small embankment reservoirs, but neither SWMM nor PCSWMM provides a native facility for simulating the failure of such a structure. Engineers analyzing dam-adjacent SWMM models therefore must export geometry to U.S. Army Corps' HEC-RAS — losing their SWMM network model — or hand-construct a deterministic `[TIMESERIES]`/`[INFLOWS]` boundary in a spreadsheet. Both options are deterministic; neither readily supports Wahl's recommended Monte Carlo workflow.

`swmm-breach` closes this workflow gap. To the author's knowledge it is the first open-source Python package to combine: (i) end-to-end EPA SWMM and PCSWMM `.inp`/`.out` integration; and (ii) Wahl-style Monte Carlo uncertainty propagation on the Froehlich [4, 5] breach regressions, with optional multi-vintage ensemble averaging across successive Froehlich updates. We use the term "multi-vintage" rather than "multi-model" because the current ensemble combines two regressions from the same author fit to overlapping calibration databases (Froehlich 1995 and Froehlich 2008); cross-family epistemic uncertainty across structurally distinct regressions (Xu and Zhang [6]; MacDonald and Langridge-Monopolis [7]) or physics-based models (NWS BREACH [9]) is planned for a subsequent release. The target user is a consulting engineer or state dam-safety reviewer running SWMM or PCSWMM who currently faces a forced choice between losing their SWMM model to HEC-RAS export or losing probabilistic rigor by hand-pasting a deterministic peak.

Related work in the empirical-regression breach literature includes Froehlich [4, 5], Xu and Zhang [6], MacDonald and Langridge-Monopolis [7], and Walder and O'Connor [8]; in physics-based breach simulation, the NWS BREACH model [9] and the synthesis by Wahl [10]. None of these have a pip-installable Python implementation integrated with SWMM I/O.

# 2. Software description

## 2.1 Software architecture

The package follows an `src/` layout. The top-level package `swmm_breach` contains eight modules: `breach` (data structures), `froehlich` and `froehlich_1995` (regression implementations), `reservoir` (storage-curve representation), `hydrograph` (level-pool routing), `swmm` (`.inp` integration), `output` (`.out` binary reader), and `uncertainty` (Monte Carlo sampler and multi-model ensemble). The runtime dependency is NumPy alone; an optional `viz` extra adds Matplotlib for plotting helpers. The package is pip-installable from the public GitHub repository and from the archived Zenodo release [11].

Both the SWMM `.inp` parser and the `.out` binary reader are implemented against the documented EPA SWMM 5 format specifications rather than wrapping `pyswmm` or `swmm-toolkit`, which keeps the runtime footprint minimal and allows reviewers to audit the implementation directly against the published format specs. The current test suite verifies the `.out` reader by round-trip against synthetic fixtures generated to the same format specification — confirming internal consistency between the writer and reader, but not, by itself, agreement with the reference EPA `swmm5` engine. End-to-end validation against `swmm5`-produced binaries on a bundled test project is on the v0.8 roadmap and a known limitation of the current release (see Section 4).

The test suite contains 56 tests including physical-correctness checks against the canonical Teton Dam (1976) failure geometry compiled by Wahl [1], round-trip tests for the SWMM parsers against synthetic fixtures, mass-balance tests for the routing integrator, statistical convergence tests for the Monte Carlo sampler, and end-to-end regression tests for all three validation cases described in Section 3. Continuous integration runs the full suite on Linux, macOS, and Windows across Python 3.9–3.12 on every commit and pull request.

## 2.2 Software functionalities

`swmm-breach` exposes five core functionalities:

**Storage-curve construction.** `load_storage_curve` parses the `[STORAGE]` and `[CURVES]` sections of an EPA SWMM 5 `.inp` file and assembles a stage-storage curve for the named node. `TABULAR` storage shapes are supported; functional shapes raise an explicit `NotImplementedError` to fail loudly rather than silently misinterpret the input.

**Breach geometry prediction.** `froehlich.predict` and `froehlich_1995.predict` implement the Froehlich [4, 5] regressions for the average bottom width and formation time of a breach, given reservoir volume, breach height, and failure mode (overtopping or piping).

**Deterministic hydrograph generation.** `simulate` routes the developing trapezoidal breach through the reservoir storage curve using a broad-crested-weir outflow relationship and an explicit mass-balance integration with a user-specified timestep.

**Probabilistic ensemble simulation.** `ensemble_simulate` draws the breach width and formation time from log-normal distributions centered on the regression's central estimate with user-specifiable log-residual standard deviations, routes each realization independently on a common time grid, and returns an `EnsembleHydrograph` object that exposes per-time-step percentile envelopes and per-realization peak distributions. The breach width and formation time residuals are sampled independently because Froehlich [4, 5] reports the standard errors of estimate for each regression separately and does not publish the joint residual covariance; users with site-specific evidence of joint structure can supply a custom sampler. Multi-vintage ensembles can sample across user-supplied regressions according to weights.

**SWMM round-trip I/O.** `format_inflows_block` emits paste-ready `[TIMESERIES]` and `[INFLOWS]` text with automatic CFS/CMS conversion and reporting-timestep decimation; `node_series` and `link_series` read the SWMM binary `.out` file for downstream-response post-processing.

# 3. Illustrative examples

The package is exercised against three reference cases spanning more than three orders of magnitude in reservoir volume (Table 1): one author-authored regulatory submittal (Anson, 2026), one published historical case (Lawn Lake, 1982), and one canonical literature compilation (Teton, 1976). The Anson case is derived from a McGill Associates, PA submittal that the author co-prepared; the case is included for its small-reservoir representativeness and is disclosed accordingly in the Conflict of Interest statement. In each case the deterministic Froehlich (2008) single-realization peak and the 5/50/95 percentiles of a 2,000-realization multi-vintage ensemble (Froehlich 2008 + Froehlich 1995, equal weights) are compared with the reference peak. All three cases are included in the package's regression test suite. Three cases is too few to validate the calibration of the 90 % predictive interval in the formal sense (which would require many cases with coverage near nominal); we therefore report the reference peak's approximate rank within the predictive distribution rather than a binary in/out flag.

**Table 1.** Validation summary across three reference cases. The "Reference percentile rank" column gives the linearly-interpolated rank of the reference peak within the 2,000-realization predictive distribution, computed between the reported 5th, 50th, and 95th percentiles. Where the reference is a published range (Teton), the rank is reported as a range; values below the 5th or above the 95th percentile are reported as "<5th" or ">95th" rather than extrapolated.

| Case                       | Reservoir volume (m³) | Reference peak (m³/s) | Reference source             | Deterministic Froehlich 2008 (m³/s, % dev) | Ensemble 5 / 50 / 95 (m³/s)     | Reference percentile rank |
|----------------------------|----------------------:|----------------------:|------------------------------|-------------------------------------------:|--------------------------------:|--------------------------:|
| Anson Lower Lagoon (2026)  |              7.9 × 10⁴ |                  122 | HEC-RAS 6.6 2D unsteady [12] |                                143 (+17 %) |                   82 / 148 / 235 |                    ≈ 32nd |
| Lawn Lake Dam (1982)       |              8.0 × 10⁵ |                  510 | Jarrett & Costa, USGS [13]   |                                351 (−31 %) |                  202 / 344 / 539 |                    ≈ 88th |
| Teton Dam (1976)           |              3.1 × 10⁸ |       50,000–80,000  | Wahl compilation [1]         |                            119,000 (+83 %) |         53,000 / 108,000 / 186,000 |   < 5th to ≈ 27th         |

For the Anson County Water Treatment Plant Lower Lagoon (state ID ANSON-057, a Class C → Class A hazard reclassification submittal to the North Carolina Division of Energy, Mineral, and Land Resources in April 2026), the HEC-RAS reference peak of 121.8 m³/s lies within the 5–95 percentile envelope at approximately the 32nd percentile of the predictive distribution; the ensemble median is within a factor of 1.21 of the HEC-RAS reference [12]. For Lawn Lake Dam, an extensively documented 1982 piping failure [13], the observed peak of 510 m³/s likewise lies within the envelope, near the 88th percentile. For Teton Dam, the canonical large-scale failure in the breach-hydrology literature, the deterministic point estimate misses the observed peak (50,000–80,000 m³/s) by approximately 80 %. The published reference range is contained within the envelope but sits in its lower tail: the lower bound (50,000 m³/s) is below the ensemble 5th percentile (53,000 m³/s) and the upper bound (80,000 m³/s) is near the 27th percentile (Figure 1). This is the practical demonstration of Wahl's [1] point that single-value breach predictions can be systematically misleading at large reservoir scale; it is not, by itself, evidence that the predictive distribution is well-calibrated at that scale.

![](../teton_ensemble.png){width=85%}

**Figure 1.** Probabilistic Teton Dam (1976) breach hydrograph: 2,000-realization multi-model ensemble (Froehlich 2008 + Froehlich 1995, equal weights). The dark line is the per-time-step median; the shaded blue band is the 5–95 percentile envelope; thin gray lines are 30 randomly sampled individual realizations; the red horizontal band shows the historically reported peak discharge of 50,000–80,000 m³/s.

Across the three cases the envelope width grows with the central estimate, which is the expected behavior of log-normal residual sampling — multiplicative spread applied to a larger central peak yields a wider absolute envelope — and may also reflect Teton's reservoir volume and breach height sitting farther from the centroid of the Froehlich calibration database. We note this because the appealing reading that the envelope "knows" when to distrust itself conflates that genuine diagnostic information with a statistical artifact of the sampling scheme. The envelope is informative about peak-discharge uncertainty under the regressions sampled; it is not, on its own, a calibrated probability that the truth lies within any particular percentile band.

# 4. Impact

`swmm-breach` operationalizes Wahl's [1] two-decade-old recommendation that breach analyses report probabilistic envelopes rather than deterministic point estimates, and it does so within the existing SWMM modeling workflow used by most North American urban-stormwater and small-watershed practitioners.

**New research questions enabled.** The modular `BreachModel` interface allows direct cross-family comparison of empirical regressions (Froehlich [4, 5], Xu and Zhang [6], MacDonald and Langridge-Monopolis [7]) and physics-based models (NWS BREACH [9]) against historical cases on a common SWMM-integrated platform. The package's per-realization peak distributions support new comparisons between within-regression parametric uncertainty and between-regression epistemic uncertainty that have been difficult to perform in spreadsheet-based workflows.

**Improvement of existing research questions.** For dam-breach formulation comparison and benchmarking studies, the reproducible test fixtures and end-to-end SWMM round-trip eliminate a significant manual effort previously required to combine breach predictions with SWMM-based downstream routing. The published ensemble envelopes for Teton, Lawn Lake, and Anson provide an immediate benchmark against which alternative formulations can be compared.

**Daily practice of users.** For consulting engineers performing dam-breach analysis as part of an EAP submittal, hazard reclassification, or floodplain delineation, probabilistic envelopes can now be reported at no additional cost over a deterministic estimate, using the same SWMM model that supports the rest of the project's hydraulic analysis. The package's `FailureMode` argument lets the same input deck be re-run under both piping and overtopping failure assumptions, providing a defensible "best-estimate to worst-reasonable" bracket without requiring the analyst to commit to a single failure scenario.

**Use within and outside the intended user group.** The package was first released publicly on 11 May 2026 and a preprint of this article was posted at EarthArXiv (submission #13032) on 13 May 2026. The repository [14] and archived Zenodo release [11] are openly available for download and use; uptake statistics are not yet meaningful given the recency of release. The package has been applied by the author to a North Carolina Department of Environmental Quality dam hazard reclassification submittal [12], which is a public record under N.C. Gen. Stat. § 132-1.

**Commercial use.** `swmm-breach` is MIT-licensed and may be used in commercial settings without restriction. No spin-off entities exist or are planned.

**Limitations and planned extensions.** The principal limitations of v0.7.0 are: (i) only the Froehlich [4, 5] regression family is implemented; cross-family regressions (Xu and Zhang [6]; MacDonald and Langridge-Monopolis [7]) and physics-based breach models (NWS BREACH [9]) are not — so the ensemble samples vintage uncertainty within one regression family, not model-form uncertainty across families; (ii) breach width and formation time residuals are sampled independently because no published joint covariance from the Froehlich fits is available, so any joint structure is unrepresented; (iii) only `SHAPE = TABULAR` SWMM storage nodes are supported (functional shapes raise `NotImplementedError`); (iv) breach growth is linear in time, which under-represents the highly non-linear headcut-driven progression observed in real failures, and the broad-crested-weir outflow does not capture the orifice-to-weir transition characteristic of early-stage overtopping failures; (v) the `.out` reader is currently verified by round-trip against synthetic fixtures and against the documented EPA SWMM 5 format spec, but end-to-end agreement with output produced by the EPA `swmm5` engine itself on a bundled test project is on the v0.8 roadmap; (vi) downstream channel attenuation between the breach outflow node and the receiving SWMM network must be handled by SWMM's native routing rather than by an external Muskingum routing layer. Planned v0.8 extensions address (i), (iii), (v), and (vi) in priority order.

# 5. Conclusions

`swmm-breach` provides probabilistic dam-breach hydrograph forecasting integrated with EPA SWMM and PCSWMM. The package implements the Froehlich [4, 5] regressions, level-pool routing through a developing trapezoidal weir, Wahl-style Monte Carlo uncertainty propagation [1], multi-vintage ensemble averaging, and end-to-end SWMM `.inp`/`.out` file integration. Across three reference cases spanning more than three orders of magnitude in reservoir volume, the 5–95 percentile envelope contains the reference peak in all three; the reference rank within the predictive distribution ranges from ≈ 32nd percentile (Anson) to ≈ 88th percentile (Lawn Lake) to a < 5th to ≈ 27th band (Teton, range reference). The deterministic single-model point estimate misses the observed Teton peak by approximately 80 %, illustrating Wahl's [1] point that single-value breach predictions can be systematically misleading at large reservoir scale. The package is, to the author's knowledge, the first open-source Python implementation of Wahl's Monte Carlo recommendation for the SWMM ecosystem.

# Acknowledgements

The author thanks the EPA SWMM development team for maintaining the SWMM source code as open and public, which made the format-specification-driven implementation of the `.inp` and `.out` integration possible.

# Conflict of interest

The author is employed as a Professional Engineer at McGill Associates, PA, which prepared the public-record Anson County hazard reclassification submittal [12] cited as a validation case. McGill Associates had no role in the design, development, or analysis of this software; `swmm-breach` was developed independently outside the author's employment. No external funding was received.

# Declaration of generative AI and AI-assisted technologies in the writing process

During the preparation of this work, the author used Anthropic's Claude (Opus 4.7) to assist with drafting and editing of manuscript text. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the publication.

# References

[1] Wahl, T. L. (2004). Uncertainty of Predictions of Embankment Dam Breach Parameters. *Journal of Hydraulic Engineering*, 130(5), 389–397. https://doi.org/10.1061/(ASCE)0733-9429(2004)130:5(389)

[2] U.S. Army Corps of Engineers. (2024). *National Inventory of Dams*. https://nid.usace.army.mil/ (accessed 12 May 2026).

[3] Rossman, L. A. (2017). *Storm Water Management Model Reference Manual, Volume II — Hydraulics.* EPA/600/R-17/111. U.S. Environmental Protection Agency, Cincinnati, OH.

[4] Froehlich, D. C. (1995). Embankment Dam Breach Parameters Revisited. In *Water Resources Engineering: Proceedings of the 1995 ASCE Conference on Water Resources Engineering*, San Antonio, TX, 887–891.

[5] Froehlich, D. C. (2008). Embankment Dam Breach Parameters and Their Uncertainties. *Journal of Hydraulic Engineering*, 134(12), 1708–1721. https://doi.org/10.1061/(ASCE)0733-9429(2008)134:12(1708)

[6] Xu, Y., and Zhang, L. M. (2009). Breaching Parameters for Earth and Rockfill Dams. *Journal of Geotechnical and Geoenvironmental Engineering*, 135(12), 1957–1970. https://doi.org/10.1061/(ASCE)GT.1943-5606.0000162

[7] MacDonald, T. C., and Langridge-Monopolis, J. (1984). Breaching Characteristics of Dam Failures. *Journal of Hydraulic Engineering*, 110(5), 567–586. https://doi.org/10.1061/(ASCE)0733-9429(1984)110:5(567)

[8] Walder, J. S., and O'Connor, J. E. (1997). Methods for predicting peak discharge of floods caused by failure of natural and constructed earthen dams. *Water Resources Research*, 33(10), 2337–2348. https://doi.org/10.1029/97WR01616

[9] Fread, D. L. (1988). *BREACH: An Erosion Model for Earthen Dam Failures.* National Weather Service, NOAA, Silver Spring, MD.

[10] Wahl, T. L. (2014). *Evaluation of Erodibility-Based Embankment Dam Breach Equations.* Hydraulic Laboratory Report HL-2014-02, U.S. Bureau of Reclamation.

[11] Flynn, M. B. (2026). *mf4633/swmm-breach: v0.7.0* (v0.7.0). Zenodo. https://doi.org/10.5281/zenodo.20172074

[12] McGill Associates, PA. (2026). *Anson County WTP Lower Lagoon (ANSON-057): Class C to Class A Hazard Reclassification Submittal.* Submitted to North Carolina Department of Environmental Quality, Division of Energy, Mineral, and Land Resources, Land Quality Section, April 2026. Public record under N.C. Gen. Stat. § 132-1.

[13] Jarrett, R. D., and Costa, J. E. (1986). *Hydrology, geomorphology, and dam-break modeling of the July 15, 1982 Lawn Lake Dam and Cascade Lake Dam failures, Larimer County, Colorado.* U.S. Geological Survey Professional Paper 1369. Washington, DC.

[14] Flynn, M. B. (2026). *swmm-breach: probabilistic dam-breach hydrograph forecasting for EPA SWMM and PCSWMM.* GitHub repository. https://github.com/mf4633/swmm-breach
