import pandas as pd
from typing import List, Tuple
from shapely.geometry import Polygon

from pytab2gis.config.table_config import TableConfig
from pytab2gis.io.excel_reader import build_geometries_from_table


def build_geometries_from_table_pipeline(
    df: pd.DataFrame,
    config: TableConfig
) -> List[Tuple[str, Polygon]]:
    """
    FINAL PIPELINE FOR EXCEL TABLES.

    This function:
    - obeys GUI column selection
    - uses the selected column to define figure limits
    - supports Excel with merged / empty cells
    - produces valid Shapely geometries
    """

    # -----------------------------
    # Build raw geometries (name, geometry)
    # -----------------------------
    geometries = build_geometries_from_table(df, config)

    # -----------------------------
    # Final sanity check
    # -----------------------------
    if not geometries:
        raise RuntimeError("No valid geometries were generated.")

    return geometries
