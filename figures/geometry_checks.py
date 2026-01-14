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
