import argparse
import os
import sys

from pytab2gis.io.excel_reader import ExcelReader
from pytab2gis.table.table_detector import TableDetector
from pytab2gis.figures.figure_builder import FigureBuilder
from pytab2gis.figures.geometry_checks import GeometryChecker
from pytab2gis.crs.crs_manager import CRSDefinition, CRSManager
from pytab2gis.export.shp_exporter import ShapefileExporter
from pytab2gis.export.zip_exporter import ZipExporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pytab2gis",
        description=(
            "PyTAB2GIS — Convert semi-structured tabular data "
            "(Excel tables) into GIS polygon geometries."
        )
    )

    parser.add_argument(
        "input",
        help="Input Excel (.xlsx) file"
    )

    parser.add_argument(
        "--component-column",
        required=True,
        help="Column name containing figure/component names"
    )

    parser.add_argument(
        "--epsg",
        type=int,
        help="EPSG code of the input coordinates (e.g. 32718)"
    )

    parser.add_argument(
        "--proj",
        help="PROJ string defining the input CRS"
    )

    parser.add_argument(
        "--sheet",
        help="Specific Excel sheet to process (default: all sheets)"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output directory"
    )

    parser.add_argument(
        "--zip",
        action="store_true",
        help="Package outputs into a ZIP archive"
    )

    parser.add_argument(
        "--min-area",
        type=float,
        default=0.0,
        help="Minimum polygon area for geometry checks (default: 0)"
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # --------------------------------------------------
    # CRS SELECTION (MANDATORY)
    # --------------------------------------------------

    if args.epsg is None and args.proj is None:
        parser.error("You must specify either --epsg or --proj.")

    crs_def = CRSDefinition(
        epsg=args.epsg,
        proj_string=args.proj
    )

    crs_manager = CRSManager(crs_def)

    print(f"[INFO] Using CRS: {crs_manager.summary()}")

    # --------------------------------------------------
    # READ EXCEL
    # --------------------------------------------------

    reader = ExcelReader(args.input)
    sheets = reader.read(sheet_name=args.sheet)

    all_figures = []

    # --------------------------------------------------
    # PROCESS EACH SHEET
    # --------------------------------------------------

    for sheet_name, df in sheets.items():
        print(f"[INFO] Processing sheet: {sheet_name}")

        detector = TableDetector(
            df=df,
            component_column=args.component_column
        )

        blocks = detector.detect_tables()
        print(f"[INFO] Detected {len(blocks)} table blocks")

        builder = FigureBuilder(crs_manager)
        checker = GeometryChecker(min_area=args.min_area)

        for block in blocks:
            try:
                fig = builder.build(block)

                # Geometry checks (warnings only)
                warnings = checker.check(fig)
                for w in warnings:
                    print(f"[WARNING] {w}")

                fig.close()
                all_figures.append(fig)

            except Exception as e:
                print(
                    f"[ERROR] Failed to build figure '{block.name}': {e}",
                    file=sys.stderr
                )

    if not all_figures:
        print("[ERROR] No valid figures were generated.", file=sys.stderr)
        sys.exit(1)

    # --------------------------------------------------
    # EXPORT SHAPEFILES
    # --------------------------------------------------

    os.makedirs(args.output, exist_ok=True)

    exporter = ShapefileExporter(args.output)
    shp_files = exporter.export(all_figures)

    print(f"[INFO] Exported {len(shp_files)} shapefiles")

    # --------------------------------------------------
    # ZIP OUTPUT (OPTIONAL)
    # --------------------------------------------------

    if args.zip:
        zip_path = os.path.join(args.output, "pytab2gis_output.zip")
        zipper = ZipExporter(zip_path)
        zipper.package(shp_files)
        print(f"[INFO] ZIP archive created: {zip_path}")


if __name__ == "__main__":
    main()
