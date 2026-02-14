# Build Notes

Attempted TeX compilation commands (environment limitation):

- `latexmk -pdf -interaction=nonstopmode manuscript.tex` (warning: latexmk not installed in this environment)
- `pdflatex -interaction=nonstopmode manuscript.tex` (warning: pdflatex not installed in this environment)

Fallback used to make PDF in this environment:

- `python3 tools/make_pdf.py`

This fallback generates `manuscript.pdf` directly from `manuscript.tex` text when a TeX distribution is unavailable.
