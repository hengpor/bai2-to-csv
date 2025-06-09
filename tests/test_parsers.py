"""Tests for the BAI2 parsers module."""

import pytest

from bai2_to_csv.models import (
    Bai2AccountTrailer,
    Bai2FileHeader,
    Bai2FileTrailer,
    Bai2GroupHeader,
    Bai2GroupTrailer,
    Bai2TransactionDetail,
    Bai2TransactionSummary,
    BaiFileHeaderModel,
)
from bai2_to_csv.parsers import (
    Bai2AccountTrailerParser,
    Bai2FileHeaderParser,
    Bai2FileTrailerParser,
    Bai2GroupHeaderParser,
    Bai2GroupTrailerParser,
    Bai2TransactionDetailParser,
    Bai2TransactionSummaryParser,
    BaiFileParser,
)


class TestBai2FileHeaderParser:
    """Test Bai2FileHeaderParser."""

    def test_parse_valid_header(self):
        """Test parsing a valid file header line."""
        parser = Bai2FileHeaderParser()
        lines = ["01,000000610,BOA12345,20250525,1400,000000001,,,2/"]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, Bai2FileHeader)
        assert result.sender_id == "000000610"
        assert result.receiver_id == "BOA12345"
        assert result.creation_date == "20250525"
        assert result.creation_time == "1400"
        assert result.file_id == "000000001"
        assert result.version_number == "2"

    def test_parse_no_header_line(self):
        """Test parsing when no header line is present."""
        parser = Bai2FileHeaderParser()
        lines = ["02,BOA12345,071000039,20250525,1,,,2/"]

        result = parser.parse(lines)

        assert result is None

    def test_parse_empty_lines(self):
        """Test parsing empty lines."""
        parser = Bai2FileHeaderParser()
        lines = []

        result = parser.parse(lines)

        assert result is None

    def test_parse_multiple_lines_takes_first(self):
        """Test parsing multiple header lines takes the first one."""
        parser = Bai2FileHeaderParser()
        lines = [
            "01,000000610,BOA12345,20250525,1400,000000001,,,2/",
            "01,000000611,BOA54321,20250526,1500,000000002,,,2/",
        ]

        result = parser.parse(lines)

        assert result is not None
        assert result.sender_id == "000000610"
        assert result.receiver_id == "BOA12345"


class TestBai2FileTrailerParser:
    """Test Bai2FileTrailerParser."""

    def test_parse_valid_trailer(self):
        """Test parsing a valid file trailer line."""
        parser = Bai2FileTrailerParser()
        lines = ["99,10000,0525,0/"]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, Bai2FileTrailer)
        assert result.file_control_total == "10000"
        assert result.number_of_groups == "0525"
        assert result.number_of_records == "0"

    def test_parse_no_trailer_line(self):
        """Test parsing when no trailer line is present."""
        parser = Bai2FileTrailerParser()
        lines = ["01,000000610,BOA12345,20250525,1400,000000001,,,2/"]

        result = parser.parse(lines)

        assert result is None


class TestBai2GroupHeaderParser:
    """Test Bai2GroupHeaderParser."""

    def test_parse_valid_group_header(self):
        """Test parsing a valid group header line."""
        parser = Bai2GroupHeaderParser()
        lines = ["02,BOA12345,071000039,20250525,1,,,2/"]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, Bai2GroupHeader)
        assert result.receiver_id == "BOA12345"
        assert result.originator_id == "071000039"
        assert result.group_status == "20250525"
        assert result.as_of_date == "1"
        assert result.as_of_time == ""
        assert result.currency_code == ""
        assert result.date_type == "2"

    def test_parse_no_group_header_line(self):
        """Test parsing when no group header line is present."""
        parser = Bai2GroupHeaderParser()
        lines = ["01,000000610,BOA12345,20250525,1400,000000001,,,2/"]

        result = parser.parse(lines)

        assert result is None


class TestBai2GroupTrailerParser:
    """Test Bai2GroupTrailerParser."""

    def test_parse_valid_group_trailer(self):
        """Test parsing a valid group trailer line."""
        parser = Bai2GroupTrailerParser()
        lines = ["98,10000,0525,0/"]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, Bai2GroupTrailer)
        assert result.group_control_total == "10000"
        assert result.number_of_accounts == "0525"
        assert result.number_of_records == "0"

    def test_parse_no_group_trailer_line(self):
        """Test parsing when no group trailer line is present."""
        parser = Bai2GroupTrailerParser()
        lines = ["01,000000610,BOA12345,20250525,1400,000000001,,,2/"]

        result = parser.parse(lines)

        assert result is None


class TestBai2AccountTrailerParser:
    """Test Bai2AccountTrailerParser."""

    def test_parse_valid_account_trailer(self):
        """Test parsing a valid account trailer line."""
        parser = Bai2AccountTrailerParser()
        lines = ["49,10000,0525/"]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, Bai2AccountTrailer)
        assert result.account_control_total == "10000"
        assert result.number_of_records == "0525"

    def test_parse_no_account_trailer_line(self):
        """Test parsing when no account trailer line is present."""
        parser = Bai2AccountTrailerParser()
        lines = ["01,000000610,BOA12345,20250525,1400,000000001,,,2/"]

        result = parser.parse(lines)

        assert result is None


class TestBai2TransactionSummaryParser:
    """Test Bai2TransactionSummaryParser."""

    def test_parse_valid_transaction_summary(self):
        """Test parsing valid transaction summary lines."""
        parser = Bai2TransactionSummaryParser()
        lines = [
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S,125351,0,0/",
            "88,110,0,0,S,0,0,0/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
        ]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 2

        # Check first transaction summary
        summary1 = result[0]
        assert isinstance(summary1, Bai2TransactionSummary)
        assert summary1.customer_account == "1234567890"
        assert summary1.currency_code == "USD"
        assert summary1.transaction_bai_code == "100"
        assert summary1.amount == "125351"
        assert summary1.transaction_code == "1"
        assert summary1.transaction_type == "S"
        assert summary1.fund_available_immediately == "125351"
        assert summary1.fund_available_in_one_day == "0"
        assert summary1.fund_available_in_two_days == "0"

    def test_parse_transaction_summary_without_fund_details(self):
        """Test parsing transaction summary without fund availability details."""
        parser = Bai2TransactionSummaryParser()
        lines = [
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
        ]

        result = parser.parse(lines)

        assert result is not None
        assert len(result) == 1

        summary = result[0]
        assert summary.customer_account == "1234567890"
        assert summary.currency_code == "USD"
        assert summary.transaction_bai_code == "100"
        assert summary.amount == "125351"
        assert summary.transaction_code == "1"
        assert summary.transaction_type == "S"
        assert summary.fund_available_immediately is None
        assert summary.fund_available_in_one_day is None
        assert summary.fund_available_in_two_days is None

    def test_get_customer_account(self):
        """Test getting customer account from account identifier line."""
        parser = Bai2TransactionSummaryParser()
        line = "03,1234567890,USD,10000/"

        account, currency = parser.get_customer_account(line)

        assert account == "1234567890"
        assert currency == "USD"

    def test_get_transaction_summary_lines(self):
        """Test getting transaction summary lines."""
        parser = Bai2TransactionSummaryParser()
        lines = [
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S,125351,0,0/",
            "88,110,0,0,S,0,0,0/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "49,10000,0525/",
        ]

        result = parser.get_transaction_summary_lines(lines)

        assert len(result) == 3  # Account identifier + 2 continuation lines
        assert result[0] == "03,1234567890,USD,10000/"
        assert result[1] == "88,100,125351,1,S,125351,0,0/"
        assert result[2] == "88,110,0,0,S,0,0,0/"


class TestBai2TransactionDetailParser:
    """Test Bai2TransactionDetailParser."""

    def test_parse_valid_transaction_detail(self):
        """Test parsing valid transaction detail lines."""
        parser = Bai2TransactionDetailParser()
        lines = [
            "03,1234567890,USD,10000/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "88,transaction text here/",
            "49,10000,0525/",
        ]

        result = parser.parse(lines)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1

        detail = result[0]
        assert isinstance(detail, Bai2TransactionDetail)
        assert detail.customer_account == "1234567890"
        assert detail.currency_code == "USD"
        assert detail.transaction_bai_code == "10000"
        assert detail.amount == "0525"
        assert detail.fund_type == "10000"
        assert detail.bank_reference == "CHECK"
        assert detail.customer_reference == "123456"
        assert detail.transaction_text == "transaction text here"

    def test_get_transaction_lines(self):
        """Test getting transaction detail lines."""
        parser = Bai2TransactionDetailParser()
        lines = [
            "03,1234567890,USD,10000/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "88,transaction text here/",
            "49,10000,0525/",
        ]

        result = parser.get_transaction_lines(lines)

        assert len(result) == 2  # Transaction detail + continuation line
        assert result[0] == "16,10000,0525,10000,000000000,CHECK,123456/"
        assert result[1] == "88,transaction text here/"


class TestBaiFileParser:
    """Test BaiFileParser - the main file parser."""

    @pytest.fixture
    def sample_bai2_lines(self):
        """Sample BAI2 file lines for testing."""
        return [
            "01,000000610,BOA12345,20250525,1400,000000001,,,2/",
            "02,BOA12345,071000039,20250525,1,,,2/",
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S,125351,0,0/",
            "88,110,0,0,S,0,0,0/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "88,transaction text/",
            "49,10000,0525/",
            "98,10000,0525,0/",
            "99,10000,0525,0/",
        ]

    def test_parse_complete_file(self, sample_bai2_lines):
        """Test parsing a complete BAI2 file."""
        parser = BaiFileParser()

        result = parser.parse(sample_bai2_lines)

        assert result is not None
        assert isinstance(result, BaiFileHeaderModel)

        # Check file header
        assert result.file_header.sender_id == "000000610"
        assert result.file_header.receiver_id == "BOA12345"

        # Check file trailer
        assert result.file_trailer.file_control_total == "10000"
        assert result.file_trailer.number_of_groups == "0525"

        # Check group headers
        assert len(result.group_headers) == 1
        group = result.group_headers[0]
        assert group.group_header.receiver_id == "BOA12345"
        assert group.group_header.originator_id == "071000039"

        # Check accounts
        assert len(group.accounts) == 1
        account = group.accounts[0]
        assert len(account.transaction_summary) == 2
        assert len(account.transaction_detail) == 1

        # Check transaction summary
        summary = account.transaction_summary[0]
        assert summary.customer_account == "1234567890"
        assert summary.currency_code == "USD"
        assert summary.transaction_bai_code == "100"

        # Check transaction detail
        detail = account.transaction_detail[0]
        assert detail.customer_account == "1234567890"
        assert detail.currency_code == "USD"
        assert detail.bank_reference == "CHECK"
        assert detail.customer_reference == "123456"

    def test_split_lines_into_groups(self, sample_bai2_lines):
        """Test splitting lines into groups."""
        parser = BaiFileParser()

        result = parser.split_lines_into_groups(sample_bai2_lines)

        assert "group_0" in result
        group_lines = result["group_0"]
        assert len(group_lines) == 8  # Lines from group header to group trailer
        assert group_lines[0].startswith("02,")  # Group header
        assert group_lines[-1].startswith("98,")  # Group trailer

    def test_split_lines_into_accounts(self):
        """Test splitting group lines into accounts."""
        parser = BaiFileParser()
        group_lines = [
            "02,BOA12345,071000039,20250525,1,,,2/",
            "03,1234567890,USD,10000/",
            "88,100,125351,1,S,125351,0,0/",
            "16,10000,0525,10000,000000000,CHECK,123456/",
            "49,10000,0525/",
            "98,10000,0525,0/",
        ]

        result = parser.split_lines_into_accounts(group_lines)

        assert "account_0" in result
        account_lines = result["account_0"]
        assert len(account_lines) == 4  # Account identifier to account trailer
        assert account_lines[0].startswith("03,")  # Account identifier
        assert account_lines[-1].startswith("49,")  # Account trailer

    def test_group_lines(self):
        """Test the generic group_lines method."""
        parser = BaiFileParser()
        lines = [
            "01,header/",
            "02,start1/",
            "03,content1/",
            "04,end1/",
            "02,start2/",
            "03,content2/",
            "04,end2/",
            "99,trailer/",
        ]

        result = parser.group_lines(lines, ["02", "03", "04"], "02", "04")

        assert len(result) == 2
        assert "group_0" in result
        assert "group_1" in result
        assert len(result["group_0"]) == 3  # start1, content1, end1
        assert len(result["group_1"]) == 3  # start2, content2, end2