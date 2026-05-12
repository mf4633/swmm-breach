# EMS submission checklist for swmm-breach

This checklist describes the user-side actions required to submit the
manuscript at `paper/ems/manuscript.md` to *Environmental Modelling & Software*
(EMS) and to post the preprint to EarthArXiv.

## A. Convert manuscript.md to .docx

EMS requires `.doc` or `.docx` (or LaTeX). Markdown is not accepted.

```bash
# Requires pandoc installed
cd paper/ems
pandoc manuscript.md -o manuscript.docx
```

Open the resulting `.docx` in Word and verify formatting (especially the
equations and the Table 1 validation summary).

## B. Generate Zenodo DOI for the v0.7.0 release

Both EMS and EarthArXiv expect a persistent identifier for the
software described.

1. Sign in to https://zenodo.org with your GitHub account.
2. Go to https://zenodo.org/account/settings/github/ and toggle ON
   the `mf4633/swmm-breach` repository.
3. On GitHub, the v0.7.0 tag should automatically trigger a Zenodo
   archive on the next push. (Alternatively, create a new GitHub
   release at https://github.com/mf4633/swmm-breach/releases/new
   targeting tag `v0.7.0`.)
4. Once Zenodo issues a DOI for v0.7.0, paste it into:
   - `manuscript.md` Software and data availability section ("[pending]")
   - The README.md (add a Zenodo badge)

## C. Post preprint to EarthArXiv

EarthArXiv (https://eartharxiv.org) is the standard preprint server
for hydrology / earth-sciences work.

1. Create an account at https://eartharxiv.org/index.php/repository/user/register
   (uses ORCID sign-in).
2. New Submission -> upload the `.docx` (or PDF export of it).
3. Authors: Michael B. Flynn (ORCID 0009-0004-2410-7950).
4. License: CC BY 4.0 (most permissive; matches the spirit of MIT).
5. Subject area: Hydrology.
6. Keywords: dam safety; breach hydrology; SWMM; PCSWMM; uncertainty
   propagation; Monte Carlo; Froehlich; Wahl.
7. Comments to editor: "Preprint accompanying manuscript submitted to
   *Environmental Modelling & Software*."
8. Submit. EarthArXiv typically posts preprints within 1-3 business days.

## D. Submit to EMS

1. Create an account at https://submit.elsevier.com/ENVSOFT (uses
   institutional or ORCID sign-in).
2. New Submission -> Article Type: **Research paper**.
3. Title, abstract, keywords: copy from `manuscript.md`.
4. Authors: Michael B. Flynn, ORCID 0009-0004-2410-7950, Independent
   researcher.
5. Manuscript: upload the `.docx`.
6. Funding statement: "No external funding was received."
7. Conflict of interest: "The author is employed at McGill Associates,
   PA, which prepared the public-record Anson County hazard
   reclassification submittal cited as a validation case. McGill had no
   role in the development of the software described in this paper."
8. Suggested reviewers (optional): consider Tony Wahl (USBR; author of
   the foundational uncertainty paper this work extends), David
   Froehlich (consultant; original regression author), or staff at the
   USACE Risk Management Center. Do not suggest anyone you have a
   personal or recent professional relationship with.
9. Cover letter (optional but recommended): a 1-paragraph statement
   that the work fills a specific gap in the open-source SWMM ecosystem
   and addresses Wahl's (2004) recommendation for probabilistic breach
   forecasting.
10. Confirm the publishing model: subscription (free) — do **not** opt
    for Gold OA unless a grant covers the $3,750 fee.
11. Submit. EMS typically returns a first decision in 8-16 weeks.

## E. After acceptance (much later)

1. Add the EMS DOI to the README.md.
2. After Elsevier's embargo (typically 12 months for AAM), upload the
   accepted manuscript to the EarthArXiv preprint as a new version.
3. Add the EMS DOI to the Zenodo record metadata.
