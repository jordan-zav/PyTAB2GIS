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

import os
import zipfile
import shutil
import tempfile
from typing import List, Tuple

import geopandas as gpd
from shapely.geometry import Polygon


# --------------------------------------------------
# Utils
# --------------------------------------------------

def _sanitize(name: str) -> str:
    return "".join(c if c.isalnum() or c in "_-" else "_" for c in name)


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


# --------------------------------------------------
# Core export
# --------------------------------------------------

def export_geometries(
    geometries: List[Tuple[str, Polygon]],
    output_dir: str,
    epsg: int,
    export_format: str,
    export_dxf: bool = False,
    zip_output: bool = False
):
    """
    export_format:
        - "SHP"
        - "GPKG"

    export_dxf:
        - True → DXF generated (requires GDAL)
        - False → no DXF

    zip_output:
        - True → outputs zipped per figure
    """

    _ensure_dir(output_dir)

    # 🔑 si es zipped, usamos un directorio temporal
    base_work_dir = (
        tempfile.mkdtemp(prefix="pytab2gis_")
        if zip_output
        else output_dir
    )

    created_folders = []

    try:
        for name, geom in geometries:
            fig = _sanitize(name)

            # -------- GPKG --------
            if export_format == "GPKG":
                path = os.path.join(output_dir, f"{fig}.gpkg")

                gdf = gpd.GeoDataFrame(
                    {"name": [name]},
                    geometry=[geom],
                    crs=f"EPSG:{epsg}"
                )
                gdf.to_file(path, driver="GPKG")
                continue

            # -------- SHP (+ optional DXF) --------
            folder = os.path.join(base_work_dir, fig)
            _ensure_dir(folder)

            # SHP (with attributes)
            shp_path = os.path.join(folder, f"{fig}.shp")

            gdf_shp = gpd.GeoDataFrame(
                {"name": [name]},
                geometry=[geom],
                crs=f"EPSG:{epsg}"
            )
            gdf_shp.to_file(shp_path, driver="ESRI Shapefile")

            if not os.path.exists(shp_path):
                raise RuntimeError(f"SHP not created: {shp_path}")

            # DXF (geometry only)
            if export_dxf:
                dxf_path = os.path.join(folder, f"{fig}.dxf")

                gdf_dxf = gpd.GeoDataFrame(
                    geometry=[geom],
                    crs=f"EPSG:{epsg}"
                )
                gdf_dxf.to_file(dxf_path, driver="DXF")

                if not os.path.exists(dxf_path):
                    raise RuntimeError(f"DXF not created: {dxf_path}")

            created_folders.append(folder)

        # -------- ZIP FINAL --------
        if zip_output:
            for folder in created_folders:
                fig = os.path.basename(folder)
                zip_path = os.path.join(output_dir, f"{fig}.zip")

                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                    for f in os.listdir(folder):
                        full_path = os.path.join(folder, f)
                        z.write(full_path, arcname=f)

    finally:
        # 🧹 limpieza total del temporal
        if zip_output and os.path.isdir(base_work_dir):
            shutil.rmtree(base_work_dir, ignore_errors=True)
