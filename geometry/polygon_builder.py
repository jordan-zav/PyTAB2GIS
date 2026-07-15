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

from shapely.geometry import Polygon
import pandas as pd
from typing import Optional


def build_polygon(
    df: pd.DataFrame,
    x_col: str = "ESTE",
    y_col: str = "NORTE"
) -> Optional[Polygon]:
    """
    Build a polygon from ordered vertices.
    Returns None if geometry is invalid.
    """

    if len(df) < 3:
        return None

    coords = list(zip(df[x_col], df[y_col]))

    # Close polygon if needed
    if coords[0] != coords[-1]:
        coords.append(coords[0])

    polygon = Polygon(coords)

    if not polygon.is_valid or polygon.area == 0:
        return None

    return polygon
