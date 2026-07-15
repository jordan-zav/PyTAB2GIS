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

from typing import Tuple, List, Optional
import unicodedata

import pandas as pd


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalizes text for robust column matching.

    - Uppercase
    - Strip whitespace
    - Remove accents
    """
    if text is None:
        return ""

    text = str(text).strip().upper()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


# --------------------------------------------------
# COLUMN FINDER
# --------------------------------------------------

class ColumnFinder:
    """
    Detects X/Y coordinate columns in a tabular dataset.

    Detection is based on semantic matching of column names,
    not on fixed positions.
    """

    # Accepted semantic keys
    X_KEYS = {
        "X", "E", "EAST", "ESTE", "COORDX", "COORD_X", "X_COORD"
    }

    Y_KEYS = {
        "Y", "N", "NORTH", "NORTE", "COORDY", "COORD_Y", "Y_COORD"
    }

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.normalized_columns = {
            col: normalize_text(col) for col in df.columns
        }

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def find_xy_columns(self) -> Tuple[str, str]:
        """
        Finds X and Y coordinate columns.

        Returns
        -------
        (x_column, y_column)

        Raises
        ------
        ValueError
            If columns cannot be uniquely identified.
        """
        x_candidates = self._find_candidates(self.X_KEYS)
        y_candidates = self._find_candidates(self.Y_KEYS)

        if not x_candidates:
            raise ValueError("No X (Easting) column detected.")

        if not y_candidates:
            raise ValueError("No Y (Northing) column detected.")

        if len(x_candidates) > 1:
            raise ValueError(
                f"Multiple X column candidates detected: {x_candidates}"
            )

        if len(y_candidates) > 1:
            raise ValueError(
                f"Multiple Y column candidates detected: {y_candidates}"
            )

        return x_candidates[0], y_candidates[0]

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------

    def _find_candidates(self, semantic_keys: set) -> List[str]:
        """
        Finds column names whose normalized form matches
        any of the semantic keys.
        """
        candidates = []

        for original, normalized in self.normalized_columns.items():
            if normalized in semantic_keys:
                candidates.append(original)

        return candidates

    # --------------------------------------------------
    # DIAGNOSTICS
    # --------------------------------------------------

    def summary(self) -> str:
        """
        Returns a short diagnostic summary.
        """
        return (
            f"Detected columns: {list(self.df.columns)} | "
            f"Normalized: {list(self.normalized_columns.values())}"
        )
