from dataclasses import dataclass
from typing import Optional, Tuple, List

import pyproj


@dataclass
class CRSDefinition:
    """
    Explicit user-defined Coordinate Reference System (CRS).

    The CRS must be provided explicitly by the user.
    No CRS inference is performed by the system.
    """
    epsg: Optional[int] = None
    proj_string: Optional[str] = None

    def to_pyproj(self) -> pyproj.CRS:
        """
        Returns a valid pyproj.CRS object.

        Raises
        ------
        ValueError
            If neither EPSG code nor PROJ string is provided.
        """
        if self.epsg is not None:
            return pyproj.CRS.from_epsg(self.epsg)

        if self.proj_string is not None:
            return pyproj.CRS.from_string(self.proj_string)

        raise ValueError("CRSDefinition requires either an EPSG code or a PROJ string.")


class CRSManager:
    """
    Handles CRS validation and basic consistency checks
    between user-defined CRS and coordinate values.
    """

    def __init__(self, crs_def: CRSDefinition):
        self.crs_def = crs_def
        self.crs = self._validate_crs()

    # --------------------------------------------------
    # CRS VALIDATION
    # --------------------------------------------------

    def _validate_crs(self) -> pyproj.CRS:
        try:
            crs = self.crs_def.to_pyproj()
        except Exception as e:
            raise ValueError(f"Invalid CRS definition: {e}")

        # If pyproj successfully creates the CRS, it is valid
        return crs

    # --------------------------------------------------
    # COORDINATE CONSISTENCY CHECKS
    # --------------------------------------------------

    def check_coordinate_ranges(
        self,
        coordinates: List[Tuple[float, float]]
    ) -> List[str]:
        """
        Performs basic consistency checks between CRS type
        and coordinate numeric ranges.

        This method never blocks execution.
        It only returns warnings.

        Parameters
        ----------
        coordinates : list of (x, y)

        Returns
        -------
        list of str
            Warning messages.
        """
        warnings = []

        if not coordinates:
            warnings.append("No coordinates provided for CRS validation.")
            return warnings

        xs, ys = zip(*coordinates)

        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)

        # Projected CRS (e.g. UTM)
        if self.crs.is_projected:
            if abs(x_max) < 180 and abs(y_max) < 90:
                warnings.append(
                    "Projected CRS selected, but coordinate values "
                    "appear to be geographic (degrees)."
                )

        # Geographic CRS
        if self.crs.is_geographic:
            if abs(x_max) > 180 or abs(y_max) > 90:
                warnings.append(
                    "Geographic CRS selected, but coordinate values "
                    "exceed degree ranges."
                )

        return warnings

    # --------------------------------------------------
    # INFO
    # --------------------------------------------------

    def summary(self) -> str:
        """
        Returns a short human-readable CRS description.
        """
        if self.crs_def.epsg is not None:
            return f"EPSG:{self.crs_def.epsg}"

        return f"PROJ: {self.crs_def.proj_string}"
