from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

from pytab2gis.crs.crs_manager import CRSManager


Coordinate = Tuple[float, float]


@dataclass
class Figure:
    """
    Represents a spatial figure defined by ordered vertices.

    A Figure is a CRS-aware spatial entity, independent of input format
    (Excel, image, etc.). Geometry construction and GIS export are handled
    in later stages of the pipeline.
    """

    name: str
    vertices: List[Coordinate]
    crs_manager: CRSManager

    source: Optional[str] = None
    table_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    # --------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------

    def validate(self) -> List[str]:
        """
        Validates the figure definition without constructing GIS geometry.

        Returns
        -------
        list of str
            List of validation error messages. Empty if valid.
        """
        errors: List[str] = []

        if not self.name or not self.name.strip():
            errors.append("Figure name is missing or empty.")

        if not self.vertices:
            errors.append("Figure has no vertices.")

        if self.vertices and len(self.vertices) < 3:
            errors.append("A figure must have at least three vertices.")

        # Coordinate type checks
        for i, v in enumerate(self.vertices):
            if not isinstance(v, tuple) or len(v) != 2:
                errors.append(f"Invalid coordinate format at index {i}: {v}")
                continue

            x, y = v
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                errors.append(f"Non-numeric coordinate at index {i}: {v}")

        return errors

    # --------------------------------------------------
    # CRS CONSISTENCY CHECKS
    # --------------------------------------------------

    def crs_warnings(self) -> List[str]:
        """
        Runs CRS-to-coordinate consistency checks.

        Returns
        -------
        list of str
            Warning messages (non-blocking).
        """
        return self.crs_manager.check_coordinate_ranges(self.vertices)

    # --------------------------------------------------
    # VERTEX OPERATIONS
    # --------------------------------------------------

    def is_closed(self) -> bool:
        """
        Checks whether the figure is already closed.

        Returns
        -------
        bool
        """
        if len(self.vertices) < 2:
            return False
        return self.vertices[0] == self.vertices[-1]

    def close(self) -> None:
        """
        Closes the figure by appending the first vertex at the end
        if not already closed.
        """
        if not self.is_closed() and self.vertices:
            self.vertices.append(self.vertices[0])

    # --------------------------------------------------
    # INFO
    # --------------------------------------------------

    def summary(self) -> str:
        """
        Returns a short textual summary of the figure.
        """
        return (
            f"Figure(name='{self.name}', "
            f"vertices={len(self.vertices)}, "
            f"CRS={self.crs_manager.summary()})"
        )
