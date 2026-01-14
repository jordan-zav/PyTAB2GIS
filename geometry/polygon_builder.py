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
