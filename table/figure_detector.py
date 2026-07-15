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

import pandas as pd
from typing import Dict, Optional


def detect_figures(
    df: pd.DataFrame,
    component_column: Optional[str] = None,
    vertex_column: str = "VERTICE"
) -> Dict[str, pd.DataFrame]:
    """
    Detect figures in a table.

    Priority:
    1) Explicit component column
    2) Vertex reset detection
    """

    # Defensive copy + clean index
    df = df.copy().reset_index(drop=True)

    # -------------------------------
    # CASE 1: Explicit component
    # -------------------------------
    if component_column and component_column in df.columns:
        return {
            str(name): group.reset_index(drop=True)
            for name, group in df.groupby(component_column)
        }

    # -------------------------------
    # CASE 2: Vertex-based detection
    # -------------------------------
    if vertex_column not in df.columns:
        raise ValueError(
            "No figure structure detected: "
            "no component column and no vertex column."
        )

    df[vertex_column] = pd.to_numeric(
        df[vertex_column], errors="coerce"
    )

    if df[vertex_column].isna().any():
        raise ValueError(
            f"Vertex column '{vertex_column}' contains non-numeric values."
        )

    figures: Dict[str, pd.DataFrame] = {}
    current_rows = []
    figure_index = 1
    prev_vertex = None

    for _, row in df.iterrows():
        vertex = row[vertex_column]

        if prev_vertex is not None and vertex <= prev_vertex:
            figures[f"figure_{figure_index}"] = pd.DataFrame(current_rows)
            figure_index += 1
            current_rows = []

        current_rows.append(row)
        prev_vertex = vertex

    if current_rows:
        figures[f"figure_{figure_index}"] = pd.DataFrame(current_rows)

    return figures
