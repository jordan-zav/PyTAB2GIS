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

from typing import List, Dict, Any, Optional
import pandas as pd


class TableBlock:
    """
    Represents a detected table block corresponding to a single figure.
    """

    def __init__(
        self,
        name: str,
        rows: pd.DataFrame,
        table_id: Optional[str] = None
    ):
        self.name = name
        self.rows = rows
        self.table_id = table_id

    def __len__(self):
        return len(self.rows)

    def summary(self) -> str:
        return (
            f"TableBlock(name='{self.name}', "
            f"rows={len(self.rows)}, "
            f"id={self.table_id})"
        )


class TableDetector:
    """
    Detects and splits a DataFrame into logical table blocks (figures).

    The detector assumes:
    - One figure = one contiguous block of rows
    - A new figure starts when a non-null component name appears
    - Component names may be inherited across rows
    """

    def __init__(
        self,
        df: pd.DataFrame,
        component_column: str
    ):
        self.df = df.copy()
        self.component_column = component_column

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def detect_tables(self) -> List[TableBlock]:
        """
        Splits the DataFrame into table blocks.

        Returns
        -------
        list of TableBlock
        """
        blocks: List[TableBlock] = []

        current_name: Optional[str] = None
        current_rows: List[int] = []
        block_counter = 1

        for idx, row in self.df.iterrows():
            component_value = row.get(self.component_column)

            # Normalize component cell
            if isinstance(component_value, str):
                component_value = component_value.strip()

            # New component detected
            if component_value not in (None, "", pd.NA):
                # Flush previous block
                if current_name is not None and current_rows:
                    block_df = self.df.loc[current_rows].copy()
                    blocks.append(
                        TableBlock(
                            name=current_name,
                            rows=block_df,
                            table_id=f"T{block_counter}"
                        )
                    )
                    block_counter += 1
                    current_rows = []

                current_name = str(component_value)

            # Skip rows until a component name is defined
            if current_name is None:
                continue

            # Skip fully empty rows
            if row.isna().all():
                continue

            current_rows.append(idx)

        # Flush last block
        if current_name is not None and current_rows:
            block_df = self.df.loc[current_rows].copy()
            blocks.append(
                TableBlock(
                    name=current_name,
                    rows=block_df,
                    table_id=f"T{block_counter}"
                )
            )

        return blocks
