# JWMM submission — format checklist & gap analysis

Source: JWMM Guide for Authors (chijournal.org/Home/ForAuthors) and the JWMM
Management Site, fetched 2026-05-27. JWMM = Journal of Water Management
Modeling, CHI. CC BY 4.0, no publication fee, authors retain copyright.

## Process
- Submit via https://management.chijournal.org/ (create account first).
- Upload: (1) the paper in the **JWMM MSWord template**, named
  `JWMM paper (Flynn).doc`; (2) the completed **Author Checklist**
  (chiwater.com/files/AuthorChecklist.pdf).
- Crossref Similarity Check runs on all submissions.
- **Double-anonymized** peer review: editor + ≥2 external reviewers.

## Hard requirements (and where we stand)

| # | JWMM requirement | Current state | Action |
|---|---|---|---|
| 1 | **MSWord JWMM template** (.doc); non-template papers returned | manuscript.md (markdown) | Final assembly is manual in Word: paste content into the CHI template, apply its styles. `manuscript.md` is the content source only. **User step** (needs the .doc template + Word). |
| 2 | **Double-anonymized** review — no author-identifying info in the paper | manuscript names author, ORCID, McGill, "a real PE engagement" | Anonymize the body: move author/ORCID/affiliation to a separate title page; describe Anson as "a 2026 NC Dam Safety reclassification submittal (public record)" without "the author prepared it." COI/funding goes in the cover letter + separate statement, not the anonymized body. (Repo/Zenodo links unavoidably de-anonymize a software paper — standard tension; keep them, note in cover letter.) |
| 3 | **Chicago Manual of Style 16th, Author-Date** | inline author-date, ad-hoc reference list | Reference list is close; normalize punctuation/italics/capitalization to Chicago author-date. |
| 4 | **Figures: JPG / PDF / TIFF / GIF — NOT PNG**; ≥300 dpi, ≥700 px wide; Arial or Times New Roman, lowercase non-bold; readable in **black & white**; caption below (CHI Caption A) | figures are PNG; teton_ensemble uses blue/red bands (not B&W-safe) | Output figures as **PDF** (vector). New PCSWMM figure built B&W-safe (line styles, not color-only). Re-export teton_ensemble to PDF + B&W-safe palette. |
| 5 | **SI units, U.S. customary in parentheses** | mixed; Anson section is cfs-primary | Make SI primary throughout; e.g. "121.8 m³/s (4,301 cfs)". |
| 6 | **Equations:** MS Equation format, centered, numbered in parentheses | LaTeX `$$` | Converts during Word assembly; number sequentially (1), (2)… **User step** in Word. |
| 7 | Title ≤ 125 characters incl. spaces | ~98 chars | OK. |
| 8 | Headings: numbered 1 / 1.1, level-3 unnumbered | already numbered 1 / 1.1 / 1.1.1 | Demote level-3 to unnumbered during Word assembly. |
| 9 | No footnotes; italics for emphasis only (no bold/underline/caps) | OK | Verify during assembly. |
| 10 | **COI disclosure:** all financial support, relationships affecting objectivity | manuscript has a Funding/COI section | Keep for the cover letter / separate statement; remove from anonymized body. |
| 11 | Original + unpublished elsewhere; disclose reproduced material | EarthArXiv preprint 13032 exists | Preprints are generally not "prior publication"; **disclose the preprint in the cover letter**. |

## Content welcome at JWMM
Urban drainage, stormwater, watershed modeling, flooding, hydraulics,
hydrology, computer programming — squarely in scope.

## No stated length/abstract-word limits (only the 125-char title cap).
