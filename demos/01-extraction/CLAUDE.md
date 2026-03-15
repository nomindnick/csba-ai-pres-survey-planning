# Act 1: PDF Extraction

## Context

This is the first stage of the CASBO 2026 demo. The audience sees 500 raw PDF
survey forms and watches them get transformed into structured data.

The survey PDFs are in `survey_pdfs/`. Each contains: respondent name, site,
position, years bands, and open-ended answers to 5 questions. About 15% use
a handwriting-style font; the rest use varied standard fonts.

## Goal

Demonstrate extraction of structured fields from PDF survey forms:
- OCR / text extraction from PDFs (including "handwritten" ones)
- Field identification and parsing
- Output as structured JSON matching the schema in `../../corpus/README.md`

## What to Show

- The messiness of real-world data (varied fonts, layouts, handwriting)
- How AI handles ambiguity and edge cases
- Validation and QC of extracted data
- The webapp page for this stage provides the visual overview; Claude Code
  does targeted live extraction of a few examples.
