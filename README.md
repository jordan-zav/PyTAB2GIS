# PyTAB2GIS

**PyTAB2GIS** is a Python-based tool for converting semi-structured tabular data
(Excel spreadsheets or table captures) into valid GIS polygon geometries.

The software is designed for mining, environmental, and engineering workflows
where spatial data are commonly delivered as tables rather than geospatial files.

PyTAB2GIS emphasizes **explicit CRS definition**, **reproducibility**, and
**robust handling of messy real-world tables**.

---

## Key Features

- Convert Excel tables directly into GIS polygons (Shapefile)
- Handle multiple figures and tables within a single sheet
- Robust detection of coordinate columns (X/Y, Easting/Northing, etc.)
- Explicit, user-defined CRS (no automatic inference)
- Geometry validation and sanity checks
- Command-line interface (CLI) and graphical user interface (GUI)
- Outputs packaged as ZIP for institutional delivery

---

## Why PyTAB2GIS?

In many mining and environmental projects, spatial features are delivered as:

- Excel spreadsheets
- copied tables from reports
- scanned or manually prepared coordinate tables

These formats lack:
- embedded CRS information
- consistent structure
- GIS-ready geometry

PyTAB2GIS bridges this gap by providing a **deterministic and auditable pipeline**
from tables to GIS-ready polygon data.

---

## Workflow Overview

Install the project in a Python environment and run either the command-line entry point or the desktop interface:

```bash
python -m pip install -e .
pytab2gis --help
python -m pytab2gis.gui.main_gui
```

## License

This project is licensed under GNU GPLv3 with a separate commercial licensing option. See `LICENSE.txt` for the open-source license terms.
