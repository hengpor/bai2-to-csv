"""Integration tests for the BAI2 to CSV converter."""

import pandas as pd
import pytest

from bai2_to_csv import Bai2Converter


class TestBai2CsvIntegration:
    """Integration tests for the complete BAI2 to CSV conversion workflow."""

    def test_end_to_end_conversion(self, sample_bai2_file, sample_csv_output_paths):
        """Test complete end-to-end conversion from BAI2 file to CSV files."""
        converter = Bai2Converter()

        # Convert the file
        summary_path, detail_path = converter.convert_file(
            str(sample_bai2_file),
            str(sample_csv_output_paths["summary"]),
            str(sample_csv_output_paths["detail"]),
        )

        # Verify files were created
        assert summary_path.exists()
        assert detail_path.exists()

        # Load and verify CSV content
        summary_df = pd.read_csv(summary_path, dtype=str)
        detail_df = pd.read_csv(detail_path, dtype=str)

        # Verify summary data structure
        assert not summary_df.empty
        expected_summary_columns = [
            "customer_account",
            "currency_code",
            "transaction_bai_code",
            "amount",
            "transaction_code",
            "transaction_type",
            "file_header_sender_id",
            "file_header_receiver_id",
            "group_header_originator_id",
        ]
        for col in expected_summary_columns:
            assert col in summary_df.columns, f"Missing column: {col}"

        # Verify detail data structure
        assert not detail_df.empty
        expected_detail_columns = [
            "customer_account",
            "currency_code",
            "transaction_bai_code",
            "amount",
            "fund_type",
            "bank_reference",
            "customer_reference",
            "transaction_text",
            "file_header_sender_id",
            "file_header_receiver_id",
            "group_header_originator_id",
        ]
        for col in expected_detail_columns:
            assert col in detail_df.columns, f"Missing column: {col}"

        # Verify specific data values
        assert summary_df["customer_account"].iloc[0] == "1234567890"
        assert summary_df["currency_code"].iloc[0] == "USD"
        assert summary_df["file_header_sender_id"].iloc[0] == "000000610"
        assert summary_df["file_header_receiver_id"].iloc[0] == "BOA12345"
        assert summary_df["group_header_originator_id"].iloc[0] == "071000039"

        assert detail_df["customer_account"].iloc[0] == "1234567890"
        assert detail_df["currency_code"].iloc[0] == "USD"
        assert detail_df["bank_reference"].iloc[0] == "CHECK"
        assert detail_df["customer_reference"].iloc[0] == "123456"

    def test_dataframe_conversion_workflow(self, sample_bai2_file):
        """Test conversion to DataFrames without file I/O."""
        converter = Bai2Converter()

        # Convert to DataFrames
        summary_df, detail_df = converter.convert_to_dataframes(str(sample_bai2_file))

        # Verify DataFrames are properly structured
        assert isinstance(summary_df, pd.DataFrame)
        assert isinstance(detail_df, pd.DataFrame)
        assert not summary_df.empty
        assert not detail_df.empty

        # Verify that all data is properly flattened and includes all headers
        assert "file_header_sender_id" in summary_df.columns
        assert "group_header_originator_id" in summary_df.columns
        assert "customer_account" in summary_df.columns

        assert "file_header_sender_id" in detail_df.columns
        assert "group_header_originator_id" in detail_df.columns
        assert "customer_account" in detail_df.columns

        # Verify data consistency between summary and detail
        assert (
            summary_df["file_header_sender_id"].iloc[0]
            == detail_df["file_header_sender_id"].iloc[0]
        )
        assert summary_df["customer_account"].iloc[0] == detail_df["customer_account"].iloc[0]

    def test_data_preservation_through_conversion(self, sample_bai2_file, sample_csv_output_paths):
        """Test that all data is preserved through the conversion process."""
        converter = Bai2Converter()

        # Convert using both methods
        summary_df1, detail_df1 = converter.convert_to_dataframes(str(sample_bai2_file))

        converter.convert_file(
            str(sample_bai2_file),
            str(sample_csv_output_paths["summary"]),
            str(sample_csv_output_paths["detail"]),
        )

        summary_df2 = pd.read_csv(sample_csv_output_paths["summary"], dtype=str)
        detail_df2 = pd.read_csv(sample_csv_output_paths["detail"], dtype=str)

        # Verify that both methods produce the same results
        pd.testing.assert_frame_equal(summary_df1, summary_df2, check_dtype=False)
        pd.testing.assert_frame_equal(detail_df1, detail_df2, check_dtype=False)

    def test_multiple_transactions_handling(self, tmp_path):
        """Test handling of multiple transactions in a BAI2 file."""
        # Create a BAI2 file with multiple transactions
        complex_bai2_content = [
            "01,000000610,BOA12345,20250525,1400,000000001,,,2/",
            "02,BOA12345,071000039,20250525,1,,,2/",
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S,125351,0,0/",
            "88,110,50000,2,C,50000,0,0/",
            "88,270,0525,1,S,0525,0,0/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "88,First transaction/",
            "16,20000,1000,20000,000000001,DEPOSIT,789012/",
            "88,Second transaction/",
            "16,30000,750,30000,000000002,TRANSFER,345678/",
            "88,Third transaction/",
            "49,10000,0525,0,0,0,1/",
            "98,10000,0525,0,0,0,1/",
            "99,10000,0525,0,0,0,1/",
        ]

        complex_bai2_file = tmp_path / "complex.bai"
        with open(complex_bai2_file, "w") as f:
            for line in complex_bai2_content:
                f.write(line + "\n")

        converter = Bai2Converter()
        summary_df, detail_df = converter.convert_to_dataframes(str(complex_bai2_file))

        # Verify multiple transactions were parsed
        assert len(summary_df) == 3  # 100, 110, 270 transaction codes
        assert len(detail_df) == 3  # 3 transaction detail records

        # Verify different transaction details
        assert "CHECK" in detail_df["bank_reference"].values
        assert "DEPOSIT" in detail_df["bank_reference"].values
        assert "TRANSFER" in detail_df["bank_reference"].values

        assert "123456" in detail_df["customer_reference"].values
        assert "789012" in detail_df["customer_reference"].values
        assert "345678" in detail_df["customer_reference"].values

    def test_error_recovery_and_validation(self, invalid_bai2_file, empty_bai2_file):
        """Test error handling and validation throughout the conversion process."""
        converter = Bai2Converter()

        # Test invalid file format
        with pytest.raises(ValueError, match="Failed to parse BAI2 file"):
            converter.convert_to_dataframes(str(invalid_bai2_file))

        # Test empty file
        with pytest.raises(ValueError, match="Input file is empty"):
            converter.convert_to_dataframes(str(empty_bai2_file))

        # Test non-existent file
        with pytest.raises(FileNotFoundError, match="Input file not found"):
            converter.convert_to_dataframes("nonexistent.bai")

    def test_csv_file_format_compliance(self, sample_bai2_file, sample_csv_output_paths):
        """Test that generated CSV files comply with standard CSV format."""
        converter = Bai2Converter()

        converter.convert_file(
            str(sample_bai2_file),
            str(sample_csv_output_paths["summary"]),
            str(sample_csv_output_paths["detail"]),
        )

        # Read files as text to check format
        summary_content = sample_csv_output_paths["summary"].read_text()
        detail_content = sample_csv_output_paths["detail"].read_text()

        # Verify CSV structure
        summary_lines = summary_content.strip().split("\n")
        detail_lines = detail_content.strip().split("\n")

        # Check headers are present
        assert len(summary_lines) >= 2  # Header + at least one data row
        assert len(detail_lines) >= 2  # Header + at least one data row

        # Check comma separation
        summary_header = summary_lines[0]
        detail_header = detail_lines[0]

        assert "," in summary_header
        assert "," in detail_header

        # Verify headers contain expected fields
        assert "customer_account" in summary_header
        assert "customer_account" in detail_header
        assert "file_header_sender_id" in summary_header
        assert "file_header_sender_id" in detail_header

        # Verify data rows have same number of columns as headers
        summary_header_cols = len(summary_header.split(","))
        detail_header_cols = len(detail_header.split(","))

        for line in summary_lines[1:]:  # Skip header
            assert len(line.split(",")) == summary_header_cols

        for line in detail_lines[1:]:  # Skip header
            assert len(line.split(",")) == detail_header_cols

    def test_large_file_handling(self, tmp_path):
        """Test handling of larger BAI2 files with multiple groups and accounts."""
        # Create a larger BAI2 file with multiple groups
        large_bai2_content = [
            "01,000000610,BOA12345,20250525,1400,000000001,,,2/",
            # Group 1
            "02,BOA12345,071000039,20250525,1,,,2/",
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S,125351,0,0/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "49,10000,0525,0,0,0,1/",
            # Group 2
            "02,BOA12345,071000040,20250525,1,,,2/",
            "03,9876543210,USD,20000/",
            "88,110,75000,1,S,75000,0,0/",
            "16,20000,1500,20000,000000001,WIRE,654321/",
            "49,20000,1500,0,0,0,1/",
            "98,20000,1500,0,0,0,1/",
            "98,10000,0525,0,0,0,1/",
            "99,30000,2025,0,0,0,2/",
        ]

        large_bai2_file = tmp_path / "large.bai"
        with open(large_bai2_file, "w") as f:
            for line in large_bai2_content:
                f.write(line + "\n")

        converter = Bai2Converter()
        summary_df, detail_df = converter.convert_to_dataframes(str(large_bai2_file))

        # Verify multiple groups were processed
        assert len(summary_df) == 2  # One summary per account
        assert len(detail_df) == 2  # One detail per account

        # Verify different accounts
        accounts = detail_df["customer_account"].unique()
        assert "1234567890" in accounts
        assert "9876543210" in accounts

        # Verify different originator IDs (indicating different groups)
        originators = summary_df["group_header_originator_id"].unique()
        assert len(originators) == 2
        assert "071000039" in originators
        assert "071000040" in originators
