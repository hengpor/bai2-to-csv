"""
BAI2 to CSV converter main module.
This module provides the main interface for converting BAI2 files to CSV format.
"""

from pathlib import Path
from typing import Tuple, Union

import pandas as pd

from .parsers import BaiFileParser


class Bai2Converter:
    """Main class for converting BAI2 files to CSV format."""

    def __init__(self) -> None:
        """Initialize the BAI2 converter."""
        self.parser = BaiFileParser()

    def convert_file(
        self,
        input_path: Union[str, Path],
        summary_output_path: Union[str, Path],
        detail_output_path: Union[str, Path],
    ) -> Tuple[Path, Path]:
        """
        Convert a BAI2 file to two CSV files: summary and detail.

        Args:
            input_path: Path to the input BAI2 file
            summary_output_path: Path where the summary CSV will be saved
            detail_output_path: Path where the detail CSV will be saved

        Returns:
            A tuple of (summary_path, detail_path) as Path objects

        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the input file is empty or invalid
        """
        summary_df, detail_df = self.convert_to_dataframes(input_path)

        summary_path = Path(summary_output_path)
        detail_path = Path(detail_output_path)
        summary_df.to_csv(summary_path, index=False)
        detail_df.to_csv(detail_path, index=False)
        return summary_path, detail_path

    def convert_to_dataframes(
        self, input_path: Union[str, Path]
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Convert a BAI2 file to pandas DataFrames without saving to CSV.

        Args:
            input_path: Path to the input BAI2 file

        Returns:
            A tuple of (summary_df, detail_df) as pandas DataFrames

        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the input file is empty or invalid
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with open(input_path, "r") as file:
            lines = file.readlines()

        if not lines:
            raise ValueError(f"Input file is empty: {input_path}")

        try:
            bai_model = self.parser.parse(lines)
            if not bai_model:
                raise ValueError(f"Failed to parse BAI2 file: {input_path}")
        except Exception as e:
            raise ValueError(f"Failed to parse BAI2 file: {str(e)}")

        summary_df, detail_df = bai_model.transform_to_dataframes()
        return self._normalize(summary_df), self._normalize(detail_df)

    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        # Pad numeric columns with leading zeros, coerce every other column to
        # cleaned strings, and replace missing values with "" so in-memory
        # frames match what CSV round-trips produce (na_filter=False).
        for col in df.columns:
            if df[col].dtype.kind in "iuf":
                df[col] = df[col].astype(str).str.zfill(9)
            else:
                df[col] = df[col].fillna("").astype(str).str.strip().str.rstrip("/")
        return df
