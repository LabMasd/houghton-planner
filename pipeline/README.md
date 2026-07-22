# Timetable extraction pipeline

Turns a festival's designed timetable PDF into the structured JSON the planner reads.
Written for the Houghton 2026 mobile timetable PDF (a vector-drawn grid, not a table).

## Run

```bash
python3 -m venv venv
./venv/bin/pip install pdfminer.six
./venv/bin/python extract3.py    # PDF -> pdf_ops.json (glyphs + vector segments, in draw order, with colors)
./venv/bin/python build3.py      # pdf_ops.json -> acts3.json (reconstruct grid cells)
./venv/bin/python finalize.py    # acts3.json -> acts_final.json (clean names, fix known garbles, dedupe)
```

Then inline `acts_final.json` into `index.html` (replace the `const DATA = {...}` blob).

## How it works / gotchas (so future-you doesn't re-learn these)

- The PDF renders **zeros as the letter "O"** ("O9:OO"). Time-label regex allows `[O0-9]`.
- Each page has an **older lineup hidden under a full-page fill**. `build3.py` cuts all
  ops before the *last* full-page fill rect, so only the current (top) layer survives.
  This is why naive text extraction produced merged/duplicate names.
- Columns come from clustering tall vertical segments by x; rows from horizontal segments
  spanning a column; cells = text glyphs between consecutive row boundaries.
- Time axis is calibrated by fitting gutter tick y-positions to minutes, then snapping
  cell boundaries to the nearest 15 min and offset-correcting to the grid.
- `finalize.py` holds a small `RENAME`/`SPLIT` table of hand-corrections for cells the
  geometry got wrong (e.g. the PDF's own "JANE FTIZ" typo, two acts sharing one cell).
  **For a new festival, expect to add a few entries here after eyeballing the output.**

## For a new festival

`extract3.py` is generic for vector-grid PDFs. `build3.py` assumes the Houghton layout
(page→day map, stage columns). A different festival's PDF will need the `PAGES` map and
possibly the column/row heuristics adjusted. The productised version (see ../RESUME.md)
turns this into a reusable tool + a CSV/paste-in path so most festivals skip PDF parsing.
