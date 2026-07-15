# Copyright (c) 2026 Jordan Zavaleta
# This file is part of PyTAB2GIS.
# PyTAB2GIS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
