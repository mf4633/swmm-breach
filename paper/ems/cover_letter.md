Michael B. Flynn
Independent researcher
Asheville, NC 28801, USA
michaelbflynn@gmail.com
ORCID: 0009-0004-2410-7950

13 May 2026

The Editors
*Environmental Modelling & Software*
Elsevier

Dear Editor,

Please find attached the manuscript "swmm-breach: Probabilistic dam-breach hydrograph forecasting integrated with EPA SWMM and PCSWMM" for consideration as a Research Paper in *Environmental Modelling & Software*.

The manuscript describes an open-source, MIT-licensed Python package that fills a specific workflow gap in the EPA SWMM ecosystem: practitioners working on dam-adjacent SWMM models currently either export their geometry to HEC-RAS (losing the SWMM network) or hand-build a deterministic boundary condition in a spreadsheet. `swmm-breach` provides end-to-end SWMM `.inp` / `.out` integration together with the first open-source Python implementation of Wahl's (2004) Monte Carlo recommendation for breach-parameter uncertainty — a recommendation widely cited in the dam-safety literature but, to the author's knowledge, not previously available to SWMM users in a directly-installable form. The package is validated against three independent reference cases spanning more than three orders of magnitude in reservoir volume (Anson lagoon 7.9 × 10⁴ m³, Lawn Lake 8.0 × 10⁵ m³, Teton Dam 3.1 × 10⁸ m³), and in every case the probabilistic 5–95 percentile envelope brackets the reference peak while the deterministic single-model point estimate misses the observed Teton peak by approximately 80 %.

I believe this work is well-aligned with *Environmental Modelling & Software*'s scope: it presents a piece of openly-distributed environmental-modelling software, documents its methods and validation in a reproducible form, and addresses a long-standing recommendation in the breach-hydrology literature that has not been operationalised in the dominant open-source environmental-modelling platform. The work complements rather than competes with established tools (HEC-RAS, PCSWMM) by occupying the open-source, probabilistic, SWMM-integrated niche.

The manuscript is original, has not been published elsewhere, and is not under consideration by any other journal. No external funding was received for the development of `swmm-breach`. The author is employed as a Professional Engineer at McGill Associates, PA, which prepared the public-record Anson County hazard reclassification submittal cited as a validation case; this is disclosed in the manuscript's Funding and Conflict of Interest statement. McGill Associates had no role in the design, development, or analysis of the software described.

Source code, test suite, and a permanent archived release (v0.7.0, Zenodo DOI [10.5281/zenodo.20172074](https://doi.org/10.5281/zenodo.20172074); concept DOI [10.5281/zenodo.20172073](https://doi.org/10.5281/zenodo.20172073)) are available at https://github.com/mf4633/swmm-breach. A preprint will be posted concurrently at EarthArXiv.

I would suggest as potential reviewers Tony L. Wahl (U.S. Bureau of Reclamation; author of the foundational uncertainty paper that motivates this work) and David C. Froehlich (consultant; original author of the regressions implemented in the package). I have no personal or recent professional relationship with either. I have no reviewers to exclude.

Thank you for considering this submission.

Sincerely,

Michael B. Flynn, P.E.
