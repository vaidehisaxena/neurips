# TabAL JMLR revision

This package contains the complete double-blind JMLR manuscript and every referenced figure.

- `main.tex`: primary JMLR source; `\anonymoustrue` is enabled for review.
- `main.pdf`: compiled 16-page manuscript.
- `jmlr2e.sty`: official JMLR style file.
- `references.bib`: complete bibliography.
- `figures/`: workflow and result figures in the manuscript's pink palette.
- `make_revision_figures.py` and `make_pink_end_figures.py`: reproducible figure-generation scripts.
- `REVIEW_RESPONSE.md`: point-by-point record of the reviewer-driven revision.

Compile from this directory with:

```bash
tectonic main.tex --keep-logs --keep-intermediates
```

The source uses the official `jmlr2e` package in preprint mode and preserves anonymous authors for review.
