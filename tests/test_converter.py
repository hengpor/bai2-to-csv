"""Tests for the BAI2 to CSV converter."""

from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from bai2_to_csv import Bai2Converter


@pytest.fixture
def sample_bai2_path() -> Path:
    """Get the path to the sample BAI2 file."""
    current_dir = Path(__file__).parent
    return current_dir / "data" / "sample.bai"


class TestBai2Converter:
    """Test Bai2Converter class."""

    def test_init(self):
        """Test converter initialization."""
        converter = Bai2Converter()
        assert converter.parser is not None

    def test_convert_file(self, tmp_path: Path, sample_bai2_path):
        """Test converting a BAI2 file to CSV."""
        converter = Bai2Converter()
        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        # Convert the file
        result_summary, result_detail = converter.convert_file(
            str(sample_bai2_path),
            str(summary_path),
            str(detail_path),
        )

        # Check that files were created
        assert result_summary.exists()
        assert result_detail.exists()
        assert result_summary == summary_path
        assert result_detail == detail_path

        # Read and check the CSV files with string data types
        summary_df = pd.read_csv(result_summary, dtype=str)
        detail_df = pd.read_csv(result_detail, dtype=str)

        # Check file header information
        assert "file_header_sender_id" in summary_df.columns
        assert "file_header_receiver_id" in summary_df.columns
        assert summary_df["file_header_sender_id"].iloc[0] == "000000610"
        assert summary_df["file_header_receiver_id"].iloc[0] == "BOA12345"

        # Check group header information
        assert "group_header_originator_id" in summary_df.columns
        assert summary_df["group_header_originator_id"].iloc[0] == "071000039"

        # Check transaction details
        assert "customer_account" in detail_df.columns
        assert "amount" in detail_df.columns
        assert "transaction_text" in detail_df.columns
        assert detail_df["customer_account"].iloc[0] == "1234567890"
        assert detail_df["amount"].iloc[0] == "0525"

    def test_convert_to_dataframes(self, sample_bai2_path):
        """Test converting a BAI2 file to DataFrames without saving."""
        converter = Bai2Converter()
        summary_df, detail_df = converter.convert_to_dataframes(str(sample_bai2_path))

        # Check summary DataFrame
        assert not summary_df.empty
        assert "customer_account" in summary_df.columns
        assert "currency_code" in summary_df.columns
        assert "transaction_bai_code" in summary_df.columns
        assert "amount" in summary_df.columns

        # Verify specific values from the sample file
        assert summary_df["customer_account"].iloc[0] == "1234567890"
        # Currency code is the 4th field in the account identifier
        # line: 03,1234567890,00000000,0,USD,10000/
        assert summary_df["currency_code"].iloc[0] == "USD"

        # Check detail DataFrame
        assert not detail_df.empty
        assert "customer_account" in detail_df.columns
        assert "amount" in detail_df.columns
        assert "transaction_text" in detail_df.columns
        assert "bank_reference" in detail_df.columns
        assert "customer_reference" in detail_df.columns

        # Verify specific values from the sample file
        assert detail_df["customer_account"].iloc[0] == "1234567890"
        assert detail_df["bank_reference"].iloc[0] == "CHECK"
        assert detail_df["customer_reference"].iloc[0] == "123456"

    def test_convert_file_path_objects(self, tmp_path: Path, sample_bai2_path):
        """Test converting using Path objects instead of strings."""
        converter = Bai2Converter()
        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        # Convert the file using Path objects
        result_summary, result_detail = converter.convert_file(
            sample_bai2_path,  # Path object
            summary_path,  # Path object
            detail_path,  # Path object
        )

        # Check that files were created
        assert result_summary.exists()
        assert result_detail.exists()

    def test_convert_to_dataframes_path_object(self, sample_bai2_path):
        """Test converting using Path object instead of string."""
        converter = Bai2Converter()

        summary_df, detail_df = converter.convert_to_dataframes(sample_bai2_path)

        assert not summary_df.empty
        assert not detail_df.empty

    def test_file_not_found_convert_file(self, tmp_path: Path):
        """Test handling of non-existent input file in convert_file."""
        converter = Bai2Converter()
        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            converter.convert_file("nonexistent.bai2", str(summary_path), str(detail_path))

    def test_file_not_found_convert_to_dataframes(self):
        """Test handling of non-existent input file in convert_to_dataframes."""
        converter = Bai2Converter()
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            converter.convert_to_dataframes("nonexistent.bai2")

    def test_empty_file_convert_file(self, tmp_path: Path):
        """Test handling of empty input file in convert_file."""
        empty_file = tmp_path / "empty.bai"
        empty_file.touch()
        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        converter = Bai2Converter()
        with pytest.raises(ValueError, match="Input file is empty"):
            converter.convert_file(str(empty_file), str(summary_path), str(detail_path))

    def test_empty_file_convert_to_dataframes(self, tmp_path: Path):
        """Test handling of empty input file in convert_to_dataframes."""
        empty_file = tmp_path / "empty.bai"
        empty_file.touch()

        converter = Bai2Converter()
        with pytest.raises(ValueError, match="Input file is empty"):
            converter.convert_to_dataframes(str(empty_file))

    def test_invalid_bai2_format_convert_file(self, tmp_path: Path):
        """Test handling of invalid BAI2 format in convert_file."""
        invalid_file = tmp_path / "invalid.bai"
        with open(invalid_file, "w") as f:
            f.write("This is not a BAI2 file\n")

        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        converter = Bai2Converter()
        with pytest.raises(ValueError, match="Failed to parse BAI2 file"):
            converter.convert_file(str(invalid_file), str(summary_path), str(detail_path))

    def test_invalid_bai2_format_convert_to_dataframes(self, tmp_path: Path):
        """Test handling of invalid BAI2 format in convert_to_dataframes."""
        invalid_file = tmp_path / "invalid.bai"
        with open(invalid_file, "w") as f:
            f.write("This is not a BAI2 file\n")

        converter = Bai2Converter()
        with pytest.raises(ValueError, match="Failed to parse BAI2 file"):
            converter.convert_to_dataframes(str(invalid_file))

    def test_parser_returns_none_convert_file(self, tmp_path: Path):
        """Test handling when parser returns None in convert_file."""
        converter = Bai2Converter()
        test_file = tmp_path / "test.bai"
        test_file.write_text("01,test/")

        # Mock the parser to return None
        with patch.object(converter.parser, "parse", return_value=None):
            summary_path = tmp_path / "summary.csv"
            detail_path = tmp_path / "detail.csv"

            with pytest.raises(ValueError, match="Failed to parse BAI2 file"):
                converter.convert_file(str(test_file), str(summary_path), str(detail_path))

    def test_parser_returns_none_convert_to_dataframes(self, tmp_path: Path):
        """Test handling when parser returns None in convert_to_dataframes."""
        converter = Bai2Converter()
        test_file = tmp_path / "test.bai"
        test_file.write_text("01,test/")

        # Mock the parser to return None
        with patch.object(converter.parser, "parse", return_value=None):
            with pytest.raises(ValueError, match="Failed to parse BAI2 file"):
                converter.convert_to_dataframes(str(test_file))

    def test_parser_exception_convert_file(self, tmp_path: Path):
        """Test handling parser exceptions in convert_file."""
        converter = Bai2Converter()
        test_file = tmp_path / "test.bai"
        test_file.write_text("01,test/")

        # Mock the parser to raise an exception
        with patch.object(converter.parser, "parse", side_effect=Exception("Parser error")):
            summary_path = tmp_path / "summary.csv"
            detail_path = tmp_path / "detail.csv"

            with pytest.raises(ValueError, match="Failed to parse BAI2 file: Parser error"):
                converter.convert_file(str(test_file), str(summary_path), str(detail_path))

    def test_parser_exception_convert_to_dataframes(self, tmp_path: Path):
        """Test handling parser exceptions in convert_to_dataframes."""
        converter = Bai2Converter()
        test_file = tmp_path / "test.bai"
        test_file.write_text("01,test/")

        # Mock the parser to raise an exception
        with patch.object(converter.parser, "parse", side_effect=Exception("Parser error")):
            with pytest.raises(ValueError, match="Failed to parse BAI2 file: Parser error"):
                converter.convert_to_dataframes(str(test_file))

    def test_data_type_preservation_convert_file(self, tmp_path: Path, sample_bai2_path):
        """Test that data types are preserved as strings in convert_file."""
        converter = Bai2Converter()
        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        converter.convert_file(str(sample_bai2_path), str(summary_path), str(detail_path))

        # Read back the CSV files
        summary_df = pd.read_csv(summary_path, dtype=str)
        detail_df = pd.read_csv(detail_path, dtype=str)

        # Check that all columns are strings
        for col in summary_df.columns:
            assert summary_df[col].dtype == "object"

        for col in detail_df.columns:
            assert detail_df[col].dtype == "object"

        # Check specific formatting
        assert summary_df["file_header_sender_id"].iloc[0] == "000000610"  # Leading zeros preserved

    def test_data_type_preservation_convert_to_dataframes(self, sample_bai2_path):
        """Test that data types are preserved as strings in convert_to_dataframes."""
        converter = Bai2Converter()
        summary_df, detail_df = converter.convert_to_dataframes(str(sample_bai2_path))

        # Check that numeric fields are formatted as strings with leading zeros
        # Note: The specific formatting depends on the implementation
        # We're checking that they are strings, not numeric types
        for col in summary_df.columns:
            assert summary_df[col].dtype == "object"

        for col in detail_df.columns:
            assert detail_df[col].dtype == "object"

    def test_csv_output_format(self, tmp_path: Path, sample_bai2_path):
        """Test the format of CSV output files."""
        converter = Bai2Converter()
        summary_path = tmp_path / "summary.csv"
        detail_path = tmp_path / "detail.csv"

        converter.convert_file(str(sample_bai2_path), str(summary_path), str(detail_path))

        # Check that CSV files are properly formatted
        summary_content = summary_path.read_text()
        detail_content = detail_path.read_text()

        # Check that files have headers (check for file_header which is the first column)
        assert summary_content.startswith("file_header_sender_id,")
        assert detail_content.startswith("file_header_sender_id,")

        # Check that files have data rows
        summary_lines = summary_content.strip().split("\n")
        detail_lines = detail_content.strip().split("\n")

        assert len(summary_lines) > 1  # Header + at least one data row
        assert len(detail_lines) > 1  # Header + at least one data row
