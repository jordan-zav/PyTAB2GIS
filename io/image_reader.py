import os
from typing import Optional

import pandas as pd
from PIL import Image
import pytesseract


class ImageTableReader:
    """
    Reads tabular data from an image using OCR and converts it
    into a pandas DataFrame.

    Intended for screenshots or scanned tables containing
    coordinate data.
    """

    def __init__(self, image_path: str, lang: str = "eng"):
        self.image_path = image_path
        self.lang = lang

        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image file not found: {self.image_path}")

        if not self.image_path.lower().endswith((".png", ".jpg", ".jpeg")):
            raise ValueError("Unsupported image format.")

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def read(self) -> pd.DataFrame:
        """
        Performs OCR on the image and returns a DataFrame.

        Returns
        -------
        pandas.DataFrame

        Raises
        ------
        RuntimeError
            If OCR extraction fails.
        """
        image = Image.open(self.image_path)

        # Basic OCR (table-like text)
        text = pytesseract.image_to_string(
            image,
            lang=self.lang,
            config="--psm 6"
        )

        if not text.strip():
            raise RuntimeError("OCR produced no readable text.")

        return self._text_to_dataframe(text)

    # --------------------------------------------------
    # INTERNAL
    # --------------------------------------------------

    def _text_to_dataframe(self, text: str) -> pd.DataFrame:
        """
        Converts OCR text output into a DataFrame.

        Strategy:
        - split lines
        - split columns by whitespace
        - keep raw structure (cleaning happens later)
        """
        lines = [l for l in text.splitlines() if l.strip()]

        rows = []
        for line in lines:
            # Split on multiple spaces / tabs
            row = line.split()
            rows.append(row)

        if not rows:
            raise RuntimeError("No table rows detected in OCR output.")

        # Pad rows to equal length
        max_len = max(len(r) for r in rows)
        rows = [r + [None] * (max_len - len(r)) for r in rows]

        df = pd.DataFrame(rows)

        # Attempt to use first row as header if it contains text
        if all(isinstance(v, str) for v in df.iloc[0]):
            df.columns = df.iloc[0]
            df = df.drop(index=0).reset_index(drop=True)

        return df
