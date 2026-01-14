import os
import pandas as pd
from shapely.geometry import Polygon, LineString
from typing import List, Tuple


class ExcelReader:
    """
    Reads Excel files and returns a dictionary of DataFrames,
    keyed by sheet name. The input file name is propagated
    to each DataFrame for downstream naming.
    """

    def __init__(self, path: str):
        self.path = path

    def read(self) -> dict:
        sheets = pd.read_excel(self.path, sheet_name=None)

        # Base name of the input file (without extension)
        base_name = os.path.splitext(os.path.basename(self.path))[0]

        for sheet_name, df in sheets.items():
            # Attach source name for geometry naming
            df._table_name = base_name

        return sheets

def build_geometries_from_table(
    df: pd.DataFrame,
    config
) -> List[Tuple[str, object]]:

    x_col = config.x_column
    y_col = config.y_column
    vertex_col = config.vertex_column
    component_col = config.component_column

    # -------------------------
    # VALIDATION
    # -------------------------
    for col in [x_col, y_col, vertex_col]:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    if component_col and component_col not in df.columns:
        raise ValueError(
            f"Selected component column not found: {component_col}"
        )

    # Preserve source table name (lost on DataFrame copy)
    table_name = getattr(df, "_table_name", None)

    df = df.copy()

    if table_name:
        df._table_name = table_name

    # Drop rows without coordinates
    df = df.dropna(subset=[x_col, y_col])

    # Ensure vertex sortable
    df[vertex_col] = df[vertex_col].astype(str).str.strip()

    def _vertex_key(v):
        try:
            return int(v)
        except Exception:
            return v

    geometries: List[Tuple[str, object]] = []

    # -------------------------
    # GROUPING LOGIC
    # -------------------------

    if component_col is not None:
        df[component_col] = df[component_col].ffill()
        groups = df.groupby(component_col)
    else:
        if not table_name:
            raise RuntimeError(
                "Internal error: input table name not available."
            )
        groups = [(table_name, df)]

    # -------------------------
    # BUILD GEOMETRIES
    # -------------------------
    for name, g in groups:
        if g.empty:
            continue

        g = g.copy()
        g["_vkey"] = g[vertex_col].apply(_vertex_key)
        g = g.sort_values("_vkey")

        coords = list(zip(g[x_col], g[y_col]))

        if len(coords) < 2:
            continue

        if len(coords) >= 3:
            geom = Polygon(coords)
            if not geom.is_valid:
                geom = geom.buffer(0)
        else:
            geom = LineString(coords)

        if geom.is_empty or not geom.is_valid:
            continue

        geometries.append((str(name), geom))

    if not geometries:
        raise RuntimeError("No valid geometries were generated.")

    return geometries
