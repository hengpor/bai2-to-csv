"""Tests for the BAI2 to CSV converter."""

from pathlib import Path

import pandas as pd
import pytest

from bai2_to_csv import Bai2Converter


@pytest.fixture
def sample_bai2_path() -> Path:
    """Get the path to the sample BAI2 file."""
    current_dir = Path(__file__).parent
    return current_dir / "data" / "sample.bai"


def test_convert_file(tmp_path: Path, sample_bai2_path):
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


def test_convert_to_dataframes(sample_bai2_path):
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


def test_file_not_found():
    """Test handling of non-existent input file."""
    converter = Bai2Converter()
    with pytest.raises(FileNotFoundError):
        converter.convert_to_dataframes("nonexistent.bai2")


def test_empty_file(tmp_path: Path):
    """Test handling of empty input file."""
    empty_file = tmp_path / "empty.bai"
    empty_file.touch()

    converter = Bai2Converter()
    with pytest.raises(ValueError, match="Input file is empty"):
        converter.convert_to_dataframes(str(empty_file))


def test_invalid_bai2_format(tmp_path: Path):
    """Test handling of invalid BAI2 format."""
    invalid_file = tmp_path / "invalid.bai"
    with open(invalid_file, "w") as f:
        f.write("This is not a BAI2 file\n")

    converter = Bai2Converter()
    with pytest.raises(ValueError, match="Failed to parse BAI2 file"):
        converter.convert_to_dataframes(str(invalid_file))
