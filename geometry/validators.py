from shapely.geometry import Polygon


def is_valid_polygon(
    polygon: Polygon,
    min_area: float = 0.0
) -> bool:
    """
    Validate a polygon geometry.

    Conditions:
    - Not None
    - Shapely valid
    - Area greater than min_area
    """

    if polygon is None:
        return False

    if not polygon.is_valid:
        return False

    if polygon.area <= min_area:
        return False

    return True
