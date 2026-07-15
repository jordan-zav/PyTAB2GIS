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

from typing import List
from shapely.geometry import Polygon
from shapely.validation import explain_validity

from pytab2gis.figures.figure_model import Figure


class GeometryChecker:
    """
    Performs basic geometric sanity checks on Figure objects
    before GIS export.
    """

    def __init__(self, min_area: float = 0.0):
        """
        Parameters
        ----------
        min_area : float
            Minimum polygon area (CRS units). Use 0 to disable.
        """
        self.min_area = min_area

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def check(self, figure: Figure) -> List[str]:
        """
        Runs geometry checks on a Figure.

        Returns
        -------
        list of str
            Warning and error messages.
        """
        messages: List[str] = []

        # Ensure enough vertices
        if len(figure.vertices) < 3:
            messages.append(
                f"Figure '{figure.name}' has fewer than 3 vertices."
            )
            return messages

        # Ensure closure
        if not figure.is_closed():
            messages.append(
                f"Figure '{figure.name}' is not closed. "
                "It will be closed automatically."
            )
            figure.close()

        # Build shapely polygon
        try:
            polygon = Polygon(figure.vertices)
        except Exception as e:
            messages.append(
                f"Failed to construct polygon for '{figure.name}': {e}"
            )
            return messages

        # Zero / near-zero area
        if polygon.area <= self.min_area:
            messages.append(
                f"Figure '{figure.name}' has zero or negligible area "
                f"(area={polygon.area})."
            )

        # Geometry validity
        if not polygon.is_valid:
            reason = explain_validity(polygon)
            messages.append(
                f"Figure '{figure.name}' has invalid geometry: {reason}"
            )

        return messages
