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
