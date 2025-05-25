"""
BAI2 to CSV converter main module.
This module provides the main interface for converting BAI2 files to CSV format.
"""

from pathlib import Path
from typing import Tuple

import pandas as pd

from .parsers import BaiFileParser


class Bai2Converter:
    """Main class for converting BAI2 files to CSV format."""

    def __init__(self):
        """Initialize the BAI2 converter."""
        self.parser = BaiFileParser()

    def convert_file(
        self,
        input_path: str,
        summary_output_path: str,
        detail_output_path: str,
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
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with open(input_path, "r") as file:
            lines = file.readlines()

        if not lines:
            raise ValueError(f"Input file is empty: {input_path}")

        # Parse the BAI2 file
        try:
            bai_model = self.parser.parse(lines)
            if not bai_model:
                raise ValueError(f"Failed to parse BAI2 file: {input_path}")
        except Exception as e:
            raise ValueError(f"Failed to parse BAI2 file: {str(e)}")

        # Convert to dataframes
        summary_df, detail_df = bai_model.transform_to_dataframes()

        # Ensure all numeric fields are treated as strings to preserve leading zeros
        for df in [summary_df, detail_df]:
            for col in df.columns:
                if df[col].dtype.kind in "iuf":  # integer, unsigned integer, or float
                    df[col] = df[col].astype(str).str.zfill(9)  # Pad with leading zeros
                elif df[col].dtype == "object":
                    df[col] = df[col].astype(str).str.strip().str.rstrip("/")

        # Save to CSV with string data types preserved
        summary_path = Path(summary_output_path)
        detail_path = Path(detail_output_path)

        summary_df.to_csv(summary_path, index=False)
        detail_df.to_csv(detail_path, index=False)

        return summary_path, detail_path

    def convert_to_dataframes(self, input_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
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

        # Parse the BAI2 file
        try:
            bai_model = self.parser.parse(lines)
            if not bai_model:
                raise ValueError(f"Failed to parse BAI2 file: {input_path}")
        except Exception as e:
            raise ValueError(f"Failed to parse BAI2 file: {str(e)}")

        # Convert to dataframes with string data types preserved
        summary_df, detail_df = bai_model.transform_to_dataframes()

        # Ensure all numeric fields are treated as strings to preserve leading zeros
        for df in [summary_df, detail_df]:
            for col in df.columns:
                if df[col].dtype.kind in "iuf":  # integer, unsigned integer, or float
                    df[col] = df[col].astype(str).str.zfill(9)  # Pad with leading zeros
                elif df[col].dtype == "object":
                    df[col] = df[col].astype(str).str.strip().str.rstrip("/")

        return summary_df, detail_df
