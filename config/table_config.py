from dataclasses import dataclass
from typing import Optional


@dataclass
class TableConfig:
    x_column: str = "ESTE"
    y_column: str = "NORTE"
    vertex_column: str = "VERTICE"
    component_column: Optional[str] = None
