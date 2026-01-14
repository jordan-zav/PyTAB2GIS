import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from pytab2gis.io.excel_reader import ExcelReader
from pytab2gis.core.pipeline import build_geometries_from_table_pipeline
from pytab2gis.config.table_config import TableConfig
from pytab2gis.export.exporter import export_geometries


class PyTAB2GIS_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyTAB2GIS — Table to GIS Converter")

        # ---- Window sizing ----
        self.root.minsize(640, 310)
        self.root.maxsize(1400, 310)  # ❌ no crecimiento vertical
        self.root.resizable(True, False)

        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=0)

        self.columns = []
        row = 0

        # -------------------------
        # INPUT FILE
        # -------------------------
        tk.Label(root, text="Input Excel (.xlsx)").grid(
            row=row, column=0, sticky="w", padx=6, pady=3
        )
        self.input_entry = tk.Entry(root)
        self.input_entry.grid(row=row, column=1, sticky="ew", padx=6, pady=3)
        tk.Button(root, text="Browse", command=self.browse_input)\
            .grid(row=row, column=2, padx=6, pady=3)

        # -------------------------
        # OUTPUT FOLDER
        # -------------------------
        row += 1
        tk.Label(root, text="Output folder").grid(
            row=row, column=0, sticky="w", padx=6, pady=3
        )
        self.output_entry = tk.Entry(root)
        self.output_entry.grid(row=row, column=1, sticky="ew", padx=6, pady=3)
        tk.Button(root, text="Browse", command=self.browse_output)\
            .grid(row=row, column=2, padx=6, pady=3)

        # -------------------------
        # COLUMN SELECTORS
        # -------------------------
        row += 1
        self._combo("X column (Easting)", row, "ESTE")

        row += 1
        self._combo("Y column (Northing)", row, "NORTE")

        row += 1
        self._combo("Vertex column", row, "VERTICE")

        row += 1
        self._combo(
            "Component column (defines figures, optional)",
            row,
            "COMPONENTE",
            help_button=True
        )

        # -------------------------
        # CRS
        # -------------------------
        row += 1
        tk.Label(
            root,
            text="Coordinate Reference System – EPSG"
        ).grid(row=row, column=0, sticky="w", padx=6, pady=3)

        crs_frame = tk.Frame(root)
        crs_frame.grid(row=row, column=1, sticky="w", padx=6, pady=3)

        self.epsg_entry = tk.Entry(crs_frame, width=8)
        self.epsg_entry.insert(0, "32718")
        self.epsg_entry.pack(side="left")

        tk.Button(
            crs_frame,
            text="ⓘ",
            width=3,
            command=self.show_crs_help
        ).pack(side="left", padx=(4, 0))

        # -------------------------
        # EXPORT OPTIONS
        # -------------------------
        row += 1
        tk.Label(root, text="Export format").grid(
            row=row, column=0, sticky="w", padx=6, pady=3
        )

        self.export_combo = ttk.Combobox(
            root,
            width=28,
            state="readonly",
            values=[
                "SHP (folders)",
                "SHP + DXF (folders)",
                "SHP + DXF (zipped)",
                "GeoPackage (GPKG)",
            ]
        )
        self.export_combo.current(1)
        self.export_combo.grid(row=row, column=1, sticky="w", padx=6, pady=3)

        # -------------------------
        # RUN
        # -------------------------
        row += 1
        tk.Button(
            root,
            text="Run PyTAB2GIS",
            command=self.run,
            bg="#4CAF50",
            fg="white",
            width=28
        ).grid(row=row, column=0, columnspan=3, pady=10)

        # -------------------------
        # FOOTER
        # -------------------------
        row += 1
        footer = tk.Frame(root)
        footer.grid(
            row=row,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(4, 4)
        )

        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)

        left = tk.Frame(footer)
        left.grid(row=0, column=0, sticky="w")

        author = tk.Label(
            left,
            text="Zavaleta, J.",
            font=("Segoe UI", 8, "underline"),
            fg="#1a73e8",
            cursor="hand2"
        )
        author.pack(side="left")
        author.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://linkedin.com/in/jordan-zav")
        )

        affiliation = tk.Label(
            left,
            text=" Geological Engineering Undergraduate Student at UNI",
            font=("Segoe UI", 8, "italic"),
            fg="#555555"
        )
        affiliation.pack(side="left")

        tk.Label(
            footer,
            text="© MIT License",
            font=("Segoe UI", 8),
            fg="#555555"
        ).grid(row=0, column=1, sticky="e")

    # --------------------------------------------------
    # UI HELPERS
    # --------------------------------------------------

    def _combo(self, label, row, default, help_button=False):
        tk.Label(self.root, text=label).grid(
            row=row, column=0, sticky="w", padx=6, pady=3
        )

        frame = tk.Frame(self.root)
        frame.grid(row=row, column=1, sticky="w", padx=6, pady=3)

        cb = ttk.Combobox(frame, width=28, state="readonly")
        cb.pack(side="left")
        cb.default_value = default

        key = label.split()[0].lower()
        setattr(self, f"{key}_combo", cb)

        if help_button:
            tk.Button(
                frame,
                text="ⓘ",
                width=3,
                command=self.show_component_help
            ).pack(side="left", padx=(4, 0))

    # --------------------------------------------------
    # HELP
    # --------------------------------------------------

    def show_crs_help(self):
        messagebox.showinfo(
            "Coordinate Reference System (CRS)",
            "Enter the EPSG code corresponding to the coordinate system of your data.\n\n"
            "Example: EPSG:32718 (UTM Zone 18S)"
        )

    def show_component_help(self):
        messagebox.showinfo(
            "Component column",
            "Defines how vertices are grouped into individual features.\n\n"
            "If left empty, all vertices are treated as a single feature."
        )

    # --------------------------------------------------
    # FILE DIALOGS
    # --------------------------------------------------

    def browse_input(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not path:
            return

        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, path)

        reader = ExcelReader(path)
        sheets = reader.read()
        first_df = next(iter(sheets.values()))
        self.columns = list(first_df.columns)

        for attr in ["x", "y", "vertex", "component"]:
            cb = getattr(self, f"{attr}_combo")
            cb["values"] = [""] + self.columns
            if cb.default_value in self.columns:
                cb.set(cb.default_value)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, path)

    # --------------------------------------------------
    # MAIN EXECUTION
    # --------------------------------------------------

    def run(self):
        try:
            input_file = self.input_entry.get()
            output_dir = self.output_entry.get()

            if not input_file or not output_dir:
                raise ValueError("Input file and output folder are required.")

            config = TableConfig(
                x_column=self.x_combo.get(),
                y_column=self.y_combo.get(),
                vertex_column=self.vertex_combo.get(),
                component_column=self.component_combo.get() or None
            )

            reader = ExcelReader(input_file)
            sheets = reader.read()

            geometries = []
            for _, df in sheets.items():
                geoms = build_geometries_from_table_pipeline(df, config)
                geometries.extend(geoms)

            if not geometries:
                raise RuntimeError("No valid geometries were generated.")

            selection = self.export_combo.get()

            if selection == "GeoPackage (GPKG)":
                export_format = "GPKG"
                export_dxf = False
                zip_output = False
            elif selection == "SHP (folders)":
                export_format = "SHP"
                export_dxf = False
                zip_output = False
            elif selection == "SHP + DXF (folders)":
                export_format = "SHP"
                export_dxf = True
                zip_output = False
            elif selection == "SHP + DXF (zipped)":
                export_format = "SHP"
                export_dxf = True
                zip_output = True
            else:
                raise ValueError("Unknown export format selection.")

            export_geometries(
                geometries=geometries,
                output_dir=output_dir,
                epsg=int(self.epsg_entry.get()),
                export_format=export_format,
                export_dxf=export_dxf,
                zip_output=zip_output
            )

            messagebox.showinfo(
                "Done",
                f"Export completed successfully.\n"
                f"Objects exported: {len(geometries)}"
            )

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    PyTAB2GIS_GUI(root)
    root.mainloop()
