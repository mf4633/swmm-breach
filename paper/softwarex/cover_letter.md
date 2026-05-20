Michael B. Flynn
Independent researcher
Asheville, NC 28801, USA
michaelbflynn@gmail.com
ORCID: 0009-0004-2410-7950

19 May 2026

The Editors
*SoftwareX*
Elsevier

Dear Editor,

Please find attached the manuscript "swmm-breach: A Python package for probabilistic dam-breach hydrograph forecasting in EPA SWMM and PCSWMM" for consideration as an Original Software Publication in *SoftwareX*.

The package addresses a specific, long-standing workflow gap in the EPA SWMM ecosystem. Engineers analyzing dam-adjacent SWMM models currently either export their geometry to HEC-RAS (losing the SWMM network) or hand-construct a deterministic boundary condition in a spreadsheet. Neither option supports Wahl's (2004) widely cited recommendation to propagate the factor-of-two to factor-of-four uncertainty inherent in the empirical breach regressions. `swmm-breach` is, to the author's knowledge, the first pip-installable Python package to combine EPA SWMM `.inp`/`.out` integration with Wahl-style Monte Carlo uncertainty propagation on the Froehlich (1995, 2008) regressions.

The submission meets the *SoftwareX* requirements:

- The software is openly available under the MIT License at https://github.com/mf4633/swmm-breach with a public issue tracker, a 56-test continuous-integration suite running on Linux, macOS, and Windows across Python 3.9–3.12, and runnable examples in `examples/`.
- An archived release of the version described in the paper (v0.7.0) is deposited at Zenodo with version DOI [10.5281/zenodo.20172074](https://doi.org/10.5281/zenodo.20172074) and concept DOI [10.5281/zenodo.20172073](https://doi.org/10.5281/zenodo.20172073).
- A preprint of the underlying methods and validation is posted at EarthArXiv (submission #13032).
- Validation is included across three independent reference cases spanning more than three orders of magnitude in reservoir volume (Anson Lower Lagoon ~10⁵ m³; Lawn Lake Dam ~10⁶ m³; Teton Dam ~10⁸ m³).

The manuscript is original, has not been published elsewhere, and is not under consideration by any other journal. No external funding was received. The author is employed as a Professional Engineer at McGill Associates, PA, which prepared the public-record Anson County hazard reclassification submittal cited as a validation case; this is disclosed in the manuscript's conflict-of-interest statement. McGill Associates had no role in the design, development, or analysis of the software.

I would suggest as potential reviewers Tony L. Wahl (U.S. Bureau of Reclamation; author of the foundational uncertainty paper that motivates this work) and David C. Froehlich (consultant; original author of the regressions implemented in the package). I have no personal or recent professional relationship with either. I have no reviewers to exclude.

Thank you for considering this submission.

Sincerely,

Michael B. Flynn, P.E.
