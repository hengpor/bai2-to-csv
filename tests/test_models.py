"""Tests for the BAI2 models module."""

import pandas as pd
import pytest
from pydantic import ValidationError

from bai2_to_csv.models import (
    Bai2AccountTrailer,
    Bai2FileHeader,
    Bai2FileTrailer,
    Bai2GroupHeader,
    Bai2GroupTrailer,
    Bai2TransactionDetail,
    Bai2TransactionSummary,
    BaiAccountModel,
    BaiFileHeaderModel,
    BaiGroupModel,
    MultiLineCodes,
    RecordCode,
)


class TestRecordCode:
    """Test RecordCode enum."""

    def test_record_codes(self):
        """Test that all record codes have correct values."""
        assert RecordCode.file_header.value == "01"
        assert RecordCode.group_header.value == "02"
        assert RecordCode.account_identifier.value == "03"
        assert RecordCode.transaction_detail.value == "16"
        assert RecordCode.account_trailer.value == "49"
        assert RecordCode.continuation.value == "88"
        assert RecordCode.group_trailer.value == "98"
        assert RecordCode.file_trailer.value == "99"


class TestMultiLineCodes:
    """Test MultiLineCodes enum."""

    def test_account_codes(self):
        """Test account codes list."""
        expected_codes = ["03", "49", "16", "88"]
        assert MultiLineCodes.account_codes.value == expected_codes

    def test_group_codes(self):
        """Test group codes list."""
        expected_codes = ["02", "98"]
        assert MultiLineCodes.group_codes.value == expected_codes


class TestBai2FileHeader:
    """Test Bai2FileHeader model."""

    def test_valid_file_header(self):
        """Test creating a valid file header."""
        header = Bai2FileHeader(
            sender_id="000000610",
            receiver_id="BOA12345",
            creation_date="20250525",
            creation_time="1400",
            file_id="000000001",
            physical_record_length="",
            block_size="",
            version_number="2",
        )
        assert header.sender_id == "000000610"
        assert header.receiver_id == "BOA12345"
        assert header.creation_date == "20250525"
        assert header.creation_time == "1400"
        assert header.file_id == "000000001"
        assert header.version_number == "2"

    def test_file_header_with_default_version(self):
        """Test file header with default version number."""
        header = Bai2FileHeader(
            sender_id="123",
            receiver_id="456",
            creation_date="20250101",
            creation_time="0800",
            file_id="001",
            physical_record_length="80",
            block_size="1024",
        )
        assert header.version_number == "2"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            Bai2FileHeader()


class TestBai2GroupHeader:
    """Test Bai2GroupHeader model."""

    def test_valid_group_header(self):
        """Test creating a valid group header."""
        header = Bai2GroupHeader(
            receiver_id="BOA12345",
            originator_id="071000039",
            group_status="20250525",
            as_of_date="20250525",
            as_of_time="1",
            currency_code="USD",
            date_type="2",
        )
        assert header.receiver_id == "BOA12345"
        assert header.originator_id == "071000039"
        assert header.currency_code == "USD"

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            Bai2GroupHeader(receiver_id="BOA12345")


class TestBai2TransactionSummary:
    """Test Bai2TransactionSummary model."""

    def test_valid_transaction_summary(self):
        """Test creating a valid transaction summary."""
        summary = Bai2TransactionSummary(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="100",
            amount="125351",
            transaction_code="1",
            transaction_type="S",
            fund_available_immediately="125351",
            fund_available_in_one_day="0",
            fund_available_in_two_days="0",
        )
        assert summary.customer_account == "1234567890"
        assert summary.currency_code == "USD"
        assert summary.transaction_bai_code == "100"
        assert summary.amount == "125351"
        assert summary.transaction_type == "S"

    def test_transaction_summary_with_optional_none(self):
        """Test transaction summary with optional fields as None."""
        summary = Bai2TransactionSummary(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="100",
            amount="125351",
            transaction_code="1",
            transaction_type="S",
        )
        assert summary.fund_available_immediately is None
        assert summary.fund_available_in_one_day is None
        assert summary.fund_available_in_two_days is None


class TestBai2TransactionDetail:
    """Test Bai2TransactionDetail model."""

    def test_valid_transaction_detail(self):
        """Test creating a valid transaction detail."""
        detail = Bai2TransactionDetail(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="10000",
            amount="0525",
            fund_type="10000",
            bank_reference="CHECK",
            customer_reference="123456",
            transaction_text="",
        )
        assert detail.customer_account == "1234567890"
        assert detail.currency_code == "USD"
        assert detail.transaction_bai_code == "10000"
        assert detail.amount == "0525"
        assert detail.bank_reference == "CHECK"
        assert detail.customer_reference == "123456"

    def test_transaction_detail_with_optional_none(self):
        """Test transaction detail with optional fields as None."""
        detail = Bai2TransactionDetail(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="10000",
            amount="0525",
            fund_type="10000",
            bank_reference="CHECK",
            customer_reference="123456",
            transaction_text="",
        )
        assert detail.fund_available_immediately is None
        assert detail.fund_available_in_one_day is None
        assert detail.fund_available_in_two_days is None


class TestBai2AccountTrailer:
    """Test Bai2AccountTrailer model."""

    def test_valid_account_trailer(self):
        """Test creating a valid account trailer."""
        trailer = Bai2AccountTrailer(account_control_total="10000", number_of_records="0525")
        assert trailer.account_control_total == "10000"
        assert trailer.number_of_records == "0525"


class TestBai2GroupTrailer:
    """Test Bai2GroupTrailer model."""

    def test_valid_group_trailer(self):
        """Test creating a valid group trailer."""
        trailer = Bai2GroupTrailer(
            group_control_total="10000",
            number_of_accounts="0525",
            number_of_records="0",
        )
        assert trailer.group_control_total == "10000"
        assert trailer.number_of_accounts == "0525"
        assert trailer.number_of_records == "0"


class TestBai2FileTrailer:
    """Test Bai2FileTrailer model."""

    def test_valid_file_trailer(self):
        """Test creating a valid file trailer."""
        trailer = Bai2FileTrailer(
            file_control_total="10000",
            number_of_groups="0525",
            number_of_records="0",
        )
        assert trailer.file_control_total == "10000"
        assert trailer.number_of_groups == "0525"
        assert trailer.number_of_records == "0"


class TestBaiFileHeaderModel:
    """Test BaiFileHeaderModel and its transformation methods."""

    @pytest.fixture
    def sample_bai_file_model(self):
        """Create a sample BaiFileHeaderModel for testing."""
        file_header = Bai2FileHeader(
            sender_id="000000610",
            receiver_id="BOA12345",
            creation_date="20250525",
            creation_time="1400",
            file_id="000000001",
            physical_record_length="",
            block_size="",
            version_number="2",
        )

        file_trailer = Bai2FileTrailer(
            file_control_total="10000",
            number_of_groups="1",
            number_of_records="5",
        )

        group_header = Bai2GroupHeader(
            receiver_id="BOA12345",
            originator_id="071000039",
            group_status="20250525",
            as_of_date="20250525",
            as_of_time="1",
            currency_code="USD",
            date_type="2",
        )

        group_trailer = Bai2GroupTrailer(
            group_control_total="10000",
            number_of_accounts="1",
            number_of_records="3",
        )

        account_trailer = Bai2AccountTrailer(
            account_control_total="10000",
            number_of_records="1",
        )

        transaction_summary = Bai2TransactionSummary(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="100",
            amount="125351",
            transaction_code="1",
            transaction_type="S",
            fund_available_immediately="125351",
            fund_available_in_one_day="0",
            fund_available_in_two_days="0",
        )

        transaction_detail = Bai2TransactionDetail(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="10000",
            amount="0525",
            fund_type="10000",
            bank_reference="CHECK",
            customer_reference="123456",
            transaction_text="",
        )

        account_model = BaiAccountModel(
            transaction_summary=[transaction_summary],
            transaction_detail=[transaction_detail],
            account_trailer=account_trailer,
        )

        group_model = BaiGroupModel(
            group_header=group_header,
            group_trailer=group_trailer,
            accounts=[account_model],
        )

        return BaiFileHeaderModel(
            file_header=file_header,
            file_trailer=file_trailer,
            group_headers=[group_model],
        )

    def test_model_transform(self, sample_bai_file_model):
        """Test the model_transform method."""
        file_header = sample_bai_file_model.file_header
        transformed = sample_bai_file_model.model_transform(file_header, "test_")

        assert "test_sender_id" in transformed
        assert "test_receiver_id" in transformed
        assert transformed["test_sender_id"] == "000000610"
        assert transformed["test_receiver_id"] == "BOA12345"

    def test_model_transform_with_index(self, sample_bai_file_model):
        """Test the model_transform method with index."""
        file_header = sample_bai_file_model.file_header
        transformed = sample_bai_file_model.model_transform(
            file_header, "test_", index=5, add_index=True
        )

        assert "_index" in transformed
        assert transformed["_index"] == 5

    def test_transform_to_dataframes(self, sample_bai_file_model):
        """Test the transform_to_dataframes method."""
        summary_df, detail_df = sample_bai_file_model.transform_to_dataframes()

        # Test summary DataFrame
        assert isinstance(summary_df, pd.DataFrame)
        assert not summary_df.empty
        assert "customer_account" in summary_df.columns
        assert "file_header_sender_id" in summary_df.columns
        assert "group_header_originator_id" in summary_df.columns
        assert summary_df["customer_account"].iloc[0] == "1234567890"
        assert summary_df["file_header_sender_id"].iloc[0] == "000000610"

        # Test detail DataFrame
        assert isinstance(detail_df, pd.DataFrame)
        assert not detail_df.empty
        assert "customer_account" in detail_df.columns
        assert "bank_reference" in detail_df.columns
        assert "customer_reference" in detail_df.columns
        assert detail_df["customer_account"].iloc[0] == "1234567890"
        assert detail_df["bank_reference"].iloc[0] == "CHECK"
        assert detail_df["customer_reference"].iloc[0] == "123456"
