# LinkedIn post — swmm-breach preprint announcement

Target: practitioner audience (dam safety engineers, stormwater modelers, state regulators). Tone: matter-of-fact, no academic puffery, no marketing language. Goal: discoverability + credibility ahead of NC Commerce call Thursday 2026-05-21.

---

## Version A — short, primary recommendation

Quick share for anyone working in dam safety or stormwater modeling:

I've posted a preprint for **swmm-breach**, an open-source Python package that gives EPA SWMM and PCSWMM users something they don't have today — a probabilistic dam-breach hydrograph generator that lives inside the SWMM workflow instead of requiring an export to HEC-RAS.

The core idea is Tony Wahl's 2004 recommendation: empirical breach regressions (Froehlich, Xu-Zhang, etc.) carry factor-of-2 to factor-of-4 uncertainty on peak discharge, so a single deterministic peak is the wrong deliverable. swmm-breach implements Monte Carlo sampling over Froehlich 1995 + 2008, routes each realization through a level-pool model, and emits a paste-ready [TIMESERIES]/[INFLOWS] block for the SWMM .inp.

Validated against three reference cases — Anson WTP lagoon (HEC-RAS 2D), Lawn Lake (USGS observed), Teton (Wahl compilation) — across more than three orders of magnitude in reservoir volume. The 5-95 percentile envelope brackets the reference peak in all three.

MIT-licensed. pip-installable. 56 tests, CI across Linux/macOS/Windows on Python 3.9-3.12.

Preprint: https://eartharxiv.org/repository/view/13032/
Code + archived release: https://github.com/mf4633/swmm-breach (Zenodo DOI 10.5281/zenodo.20172073)

Happy to take feedback before the journal version lands — especially from practitioners who run SWMM dam-adjacent.

#DamSafety #SWMM #PCSWMM #Stormwater #OpenSource

---

## Version B — shorter, lower-context

Posted a preprint for an open-source tool I've been building on the side: **swmm-breach** — probabilistic dam-breach hydrographs for EPA SWMM and PCSWMM, implementing Wahl's (2004) Monte Carlo recommendation that hasn't been operationalized in the SWMM ecosystem in the 20+ years since.

Three validation cases (Anson lagoon, Lawn Lake, Teton) — 5-95 percentile envelope brackets the reference peak across three orders of magnitude in reservoir volume.

MIT, pip-installable, 56 tests, CI across three OSes.

Preprint: https://eartharxiv.org/repository/view/13032/
Repo: https://github.com/mf4633/swmm-breach

#DamSafety #SWMM #PCSWMM #OpenSource

---

## Posting guidance

- Post Tuesday afternoon or Wednesday morning — gives it ~24 hours of feed time before Thursday 10am call.
- Tag in comments rather than the body: ASDSO, AWRA, EWRI/ASCE Dam Safety committee, anyone you know on the NC DEMLR side.
- If anyone with dam-safety reach engages (Wahl, Froehlich, USACE RMC, Schnabel, Kleinschmidt, etc.), screenshot it — concrete engagement is more persuasive than the post itself in a Commerce meeting.
- Don't pin or pay to promote. Organic-only reads more credible.
