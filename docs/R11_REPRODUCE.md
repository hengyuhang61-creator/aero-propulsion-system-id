# Reproduce the R11 offline analysis

Python 3.12+; synthetic tests and pressure comparison use the standard library. Only the native closed-field reader requires NumPy and h5py. It is deliberately restricted to these 2D quad, single-phase, single-zone snapshots; not a general Fluent converter. It reads files in `r` mode, checks input hashes before/after and requires a new output directory. Never read an HDF snapshot while Fluent/MPI or another process may be writing it.

```bash
python -m unittest discover -s experiments/sajben_study2/tests -v
python -m unittest discover -s cfd/tests -v
python cfd/closed_field_audit.py --stem /closed/case_without_suffix --out /new/r03_best
```

The stem means paired `.cas.h5` and `.dat.h5`. Repeat only the offline reader for the existing R09 endpoints if authorized assets are available. This does not run a solver. Mass flux, boundary-state enthalpy, region cuts, wall values and geometry diagnostics are written separately; exact interior energy flux is unavailable.

Obtain [p.top.5sst.gen](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif03/p.top.5sst.gen) and [p.bot.5sst.gen](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif03/p.bot.5sst.gen), following [Study #3](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif03/transdif03.html). Reuse an existing [experimental weak pressure file](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif02/sajwpres.data). Verify hashes against [the aggregate](../cfd/r11_reference_summary.json). Use numeric files, not figures.

```bash
python experiments/sajben_study2/compare_reference.py --nasa-dir /sources/study3 --experiment /sources/sajwpres.data --local /new/r03_best/wall_fields.csv --local /new/r09_control/wall_fields.csv --local /new/r09_test/wall_fields.csv --out /new/reference
```

Local parent-directory names label cases. The script checks source point counts/order and local station uniqueness, uses common experimental stations without extrapolation, and writes `reference_summary.json` and `reference_comparison.csv`. The full point table is private/local to respect source redistribution boundaries; the public repository contains original code and derived aggregates. The local R11 delivery also supplies the exact driver, log reconciliation script, source manifest and an independent NumPy interpolation/metric check. No native simulator binary or third-party code is published.
