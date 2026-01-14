from typing import List, Tuple

import pandas as pd

from pytab2gis.table.column_finder import ColumnFinder
from pytab2gis.table.table_detector import TableBlock
from pytab2gis.figures.figure_model import Figure
from pytab2gis.crs.crs_manager import CRSManager


class FigureBuilder:
    """
    Builds Figure objects from detected TableBlock instances.

    This class is responsible for:
    - detecting coordinate columns
    - extracting numeric vertex data
    - instantiating validated Figure objects
    """

    def __init__(self, crs_manager: CRSManager):
        self.crs_manager = crs_manager

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def build(self, block: TableBlock) -> Figure:
        """
        Builds a Figure from a TableBlock.

        Parameters
        ----------
        block : TableBlock

        Returns
        -------
        Figure

        Raises
        ------
        ValueError
            If the table block cannot produce a valid Figure.
        """
        df = block.rows.copy()

        # Detect X/Y columns
        finder = ColumnFinder(df)
        x_col, y_col = finder.find_xy_columns()

        # Extract coordinates
        vertices = self._extract_vertices(df, x_col, y_col)

        # Instantiate Figure
        figure = Figure(
            name=block.name,
            vertices=vertices,
            crs_manager=self.crs_manager,
            table_id=block.table_id
        )

        # Validate figure
        errors = figure.validate()
        if errors:
            raise ValueError(
                f"Invalid figure '{block.name}': " + "; ".join(errors)
            )

        return figure

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------

    def _extract_vertices(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str
    ) -> List[Tuple[float, float]]:
        """
        Extracts numeric vertex coordinates from the table.

        Non-numeric or missing values are skipped.
        """
        vertices: List[Tuple[float, float]] = []

        for idx, row in df.iterrows():
            x = row.get(x_col)
            y = row.get(y_col)

            try:
                x_val = float(x)
                y_val = float(y)
            except (TypeError, ValueError):
                # Skip rows without valid numeric coordinates
                continue

            vertices.append((x_val, y_val))

        return vertices
