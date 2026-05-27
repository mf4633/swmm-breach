# Cover letter — submission to the Journal of Water Management Modeling

To the Editor, Journal of Water Management Modeling (JWMM):

I am pleased to submit an original paper, *"swmm-breach: Probabilistic
dam-breach hydrograph forecasting integrated with EPA SWMM and PCSWMM,"*
for consideration in JWMM.

EPA SWMM and PCSWMM together dominate North American stormwater and
small-watershed modeling practice, yet neither provides a native facility
for simulating the failure of an embankment dam, detention basin, or
sludge lagoon represented as a SWMM storage node. A practitioner who needs
a breach hydrograph today must either export the geometry to HEC-RAS —
abandoning the SWMM network model in the process — or hand-build a
deterministic boundary condition in a spreadsheet. The paper presents
`swmm-breach`, an open-source (MIT) Python package that fills this gap: it
predicts breach geometry from the Froehlich (1995, 2008) regressions,
routes the breach level-pool through the storage curve parsed directly from
the project `.inp`, and writes a paste-ready `[TIMESERIES]`/`[INFLOWS]`
boundary back into the same model. It also implements Wahl's (2004)
long-standing recommendation — Monte Carlo propagation of breach-parameter
uncertainty — which routine practice still rarely follows.

I believe the paper fits JWMM's applied, SWMM/PCSWMM-centered readership
well. The lead validation case is a real North Carolina Dam Safety hazard
reclassification (Anson County WTP Lower Lagoon, ANSON-057): the package's
probabilistic envelope brackets the project's independent HEC-RAS 6.6 2D
peak, and the paper shows the breach routed in a complete EPA SWMM model
that is distributed with the package and opens unchanged in PCSWMM
Professional 2D. Two further cases (Lawn Lake 1982; Teton 1976) span more
than three orders of magnitude in reservoir volume.

**Originality and prior dissemination.** The work is original and is not
under consideration at any other journal. An earlier version is posted as a
preprint on EarthArXiv (no. 13032, CC BY 4.0); per JWMM policy I note this
preprint here. The software is archived on Zenodo and developed openly at
https://github.com/mf4633/swmm-breach.

**Funding and conflict of interest.** No external funding supported this
work. I am employed as a Professional Engineer at McGill Associates, PA,
which prepared the public-record Anson County reclassification submittal
cited as a validation case (the submittal and its underlying parameters are
public records under N.C. Gen. Stat. § 132-1). McGill Associates had no
role in the design, development, or analysis of the software, which was
developed independently outside that employment. I declare no other
conflicts of interest.

The manuscript text has been prepared in an anonymized form for
double-anonymized review; author identity and the above disclosures are
provided separately on the title page and in this letter.

Thank you for your consideration.

Sincerely,

Michael B. Flynn, P.E.
ORCID 0009-0004-2410-7950
Asheville, NC, USA
michaelbflynn@gmail.com
