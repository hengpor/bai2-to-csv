"""
BAI2 file parsers.
This module contains parser classes for parsing BAI2 file lines.
"""

import abc
from typing import Dict, List, Optional, Tuple, TypeVar, Union, cast, Generic, Sequence

from .models import (
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
    BaseModel,
    RecordCode,
)

ModelType = TypeVar("ModelType", bound=BaseModel)
ListModelType = TypeVar("ListModelType", bound=BaseModel)


def clean_line(line: str) -> List[str]:
    """Clean and split a BAI2 line into fields."""
    # Remove trailing slash and whitespace
    line = line.strip().rstrip("/")
    # Split by comma and clean each field
    return [field.strip().rstrip("/") for field in line.split(",")]


def clean_value(value: str) -> str:
    """Clean a value by removing trailing slashes and whitespace."""
    return value.strip().rstrip("/")


class Bai2ParserBase(Generic[ModelType], abc.ABC):
    """Base class for BAI2 parsers."""

    code: Optional[str] = None

    @abc.abstractmethod
    def parse(self, lines: List[str]) -> Optional[ModelType]:
        """Parse BAI2 file lines into a model."""
        raise NotImplementedError("Method not implemented")


class Bai2SingleModelParser(Bai2ParserBase[ModelType], abc.ABC):
    """Parser for single-line BAI2 records."""

    pass


class Bai2MultiLinesModelParser(Generic[ListModelType], abc.ABC):
    """Parser for multi-line BAI2 records."""

    code: Optional[str] = None
    continue_code = RecordCode.continuation.value
    end_code: Optional[str] = None

    @abc.abstractmethod
    def parse(self, lines: List[str]) -> Optional[List[ListModelType]]:
        """Parse multi-line BAI2 records into models."""
        raise NotImplementedError("Method not implemented")


class Bai2FileHeaderParser(Bai2SingleModelParser[Bai2FileHeader]):
    """Parser for BAI2 file header records."""

    code = RecordCode.file_header.value

    def parse(self, lines: List[str]) -> Optional[Bai2FileHeader]:
        """Parse BAI2 file header record."""
        for line in lines:
            data = clean_line(line)
            if data[0] == self.code:
                return Bai2FileHeader(
                    sender_id=str(data[1]).zfill(9),  # Ensure 9 digits with leading zeros
                    receiver_id=str(data[2]),  # Preserve leading zeros
                    creation_date=data[3],
                    creation_time=data[4],
                    file_id=data[5],
                    physical_record_length=data[6] or "",
                    block_size=data[7] or "",
                    version_number=data[8] if len(data) > 8 else "2",
                )
        return None


class Bai2FileTrailerParser(Bai2SingleModelParser[Bai2FileTrailer]):
    """Parser for BAI2 file trailer records."""

    code = RecordCode.file_trailer.value

    def parse(self, lines: List[str]) -> Optional[Bai2FileTrailer]:
        """Parse BAI2 file trailer record."""
        for line in lines:
            data = line.split(",")
            if data[0] == self.code:
                return Bai2FileTrailer(
                    file_control_total=data[1],
                    number_of_groups=data[2],
                    number_of_records=data[3],
                    number_of_credits="0",
                    total_credits="0",
                    number_of_debits="0",
                )
        return None


class Bai2GroupHeaderParser(Bai2SingleModelParser[Bai2GroupHeader]):
    """Parser for BAI2 group header records."""

    code = RecordCode.group_header.value

    def parse(self, lines: List[str]) -> Optional[Bai2GroupHeader]:
        """Parse BAI2 group header record."""
        for line in lines:
            data = line.split(",")
            if data[0] == self.code:
                return Bai2GroupHeader(
                    receiver_id=data[1],
                    originator_id=data[2],
                    group_status=data[3],
                    as_of_date=data[4],
                    as_of_time=data[5],
                    currency_code=data[6],
                    date_type=data[7],
                )
        return None


class Bai2GroupTrailerParser(Bai2SingleModelParser[Bai2GroupTrailer]):
    """Parser for BAI2 group trailer records."""

    code = RecordCode.group_trailer.value

    def parse(self, lines: List[str]) -> Optional[Bai2GroupTrailer]:
        """Parse BAI2 group trailer record."""
        for line in lines:
            data = line.split(",")
            if data[0] == self.code:
                return Bai2GroupTrailer(
                    group_control_total=data[1],
                    number_of_accounts=data[2],
                    number_of_records=data[3],
                    number_of_credits="0",
                    total_credits="0",
                    number_of_debits="0",
                )
        return None


class Bai2AccountTrailerParser(Bai2SingleModelParser[Bai2AccountTrailer]):
    """Parser for BAI2 account trailer records."""

    code = RecordCode.account_trailer.value

    def parse(self, lines: List[str]) -> Optional[Bai2AccountTrailer]:
        """Parse BAI2 account trailer record."""
        for line in lines:
            data = line.split(",")
            if data[0] == self.code:
                return Bai2AccountTrailer(
                    account_control_total=data[1],
                    number_of_records=data[2],
                    number_of_credits="0",
                    total_credits="0",
                    number_of_debits="0",
                    total_debits="0",
                )
        return None


class Bai2TransactionSummaryParser(Bai2MultiLinesModelParser[Bai2TransactionSummary]):
    """Parser for BAI2 transaction summary records."""

    code = RecordCode.account_identifier.value
    end_code = RecordCode.transaction_detail.value

    def parse(self, lines: List[str]) -> Optional[List[Bai2TransactionSummary]]:
        """Parse BAI2 transaction summary records."""
        account_summary_lines = self.get_transaction_summary_lines(lines)
        if not account_summary_lines:
            return None

        customer_account, currency_code = self.get_customer_account(account_summary_lines[0])
        transaction_summary_details = self.get_transaction_summary_items(account_summary_lines[1:])
        account_summary_objects: List[Bai2TransactionSummary] = []
        for details in transaction_summary_details:
            if details:  # Skip empty details
                summary = self.parse_transaction_summary_object(customer_account, currency_code, details)
                if summary:
                    account_summary_objects.append(summary)
        return account_summary_objects

    def parse_transaction_summary_object(
        self, customer_acc: str, currency_code: str, details: Dict[str, str]
    ) -> Optional[Bai2TransactionSummary]:
        """Parse a single transaction summary object."""
        return Bai2TransactionSummary(
            customer_account=str(customer_acc).zfill(10),  # Ensure 10 digits with leading zeros
            currency_code=currency_code,
            transaction_bai_code=details["transaction_bai_code"],
            amount=details["amount"],
            transaction_code=details.get("transaction_code", ""),
            transaction_type=details.get("transaction_type", ""),
            fund_available_immediately=details.get("fund_available_immediately"),
            fund_available_in_one_day=details.get("fund_available_in_one_day"),
            fund_available_in_two_days=details.get("fund_available_in_two_days"),
        )

    def get_transaction_summary_items(self, lines: List[str]) -> List[Dict[str, str]]:
        """Extract transaction summary items from lines."""
        transaction_details = []
        for line in lines:
            data = clean_line(line)
            if len(data) < 2:  # Skip invalid lines
                continue

            # Handle continuation records
            if data[0] == self.continue_code:
                details: Dict[str, str] = {
                    "transaction_bai_code": clean_value(data[1]),
                    "amount": clean_value(data[2]) if len(data) > 2 else "0",
                    "transaction_code": clean_value(data[3]) if len(data) > 3 else "",
                    "transaction_type": clean_value(data[4]) if len(data) > 4 else "",
                }

                if len(data) > 5:
                    details.update(
                        {
                            "fund_available_immediately": clean_value(data[5]),
                            "fund_available_in_one_day": clean_value(data[6]) if len(data) > 6 else "",
                            "fund_available_in_two_days": clean_value(data[7]) if len(data) > 7 else "",
                        }
                    )
                transaction_details.append(details)

        return transaction_details

    def get_customer_account(self, line: str) -> Tuple[str, str]:
        """Extract customer account and currency code from line."""
        data = clean_line(line)
        # Format: 03,account,balance,currency
        if len(data) < 4:
            raise ValueError(f"Invalid account identifier record: {line}")

        # Get the currency code from the group header if available
        currency_code = "USD"  # Default to USD if not specified
        for i, field in enumerate(data):
            if field == "USD":
                currency_code = field
                break

        return data[1], currency_code

    def get_transaction_summary_lines(self, lines: List[str]) -> List[str]:
        """Get all lines related to transaction summary."""
        account_summary_lines = []
        for line in lines:
            data = line.split(",")
            if data[0] == self.code or data[0] == self.continue_code:
                account_summary_lines.append(line)
            if data[0] == self.end_code:
                break
        return account_summary_lines


class Bai2TransactionDetailParser(Bai2MultiLinesModelParser[Bai2TransactionDetail]):
    """Parser for BAI2 transaction detail records."""

    code = RecordCode.transaction_detail.value
    end_code = RecordCode.account_trailer.value

    def parse(self, lines: List[str]) -> Optional[List[Bai2TransactionDetail]]:
        """Parse BAI2 transaction detail records."""
        transaction_lines = self.get_transaction_lines(lines)
        if not transaction_lines:
            return None

        customer_account, currency_code = self.get_customer_account(transaction_lines[0])
        grouped_lines = self.group_lines_into_transaction(transaction_lines[1:])
        transaction_details: List[Bai2TransactionDetail] = []

        for _, group in grouped_lines.items():
            transaction = self.parse_group_to_transaction(group, customer_account, currency_code)
            if transaction:
                transaction_details.append(transaction)

        return transaction_details

    def parse_group_to_transaction(
        self, lines: List[str], customer_account: str, currency_code: str
    ) -> Optional[Bai2TransactionDetail]:
        """Parse a group of lines into a transaction detail."""
        if not lines:
            return None

        data = clean_line(lines[0])
        if len(data) < 4:
            return None

        # Extract required fields
        transaction_bai_code = clean_value(data[1])
        amount = clean_value(data[2])
        fund_type = clean_value(data[3])
        bank_reference = clean_value(data[4]) if len(data) > 4 else ""
        customer_reference = clean_value(data[5]) if len(data) > 5 else ""
        text = clean_value(data[6]) if len(data) > 6 else ""

        # Handle continuation records for funds availability
        funds_data = {"immediate": "", "one_day": "", "two_days": ""}
        for line in lines[1:]:
            data = clean_line(line)
            if data[0] == self.continue_code and len(data) > 3:
                funds_data["immediate"] = clean_value(data[1])
                funds_data["one_day"] = clean_value(data[2]) if len(data) > 2 else ""
                funds_data["two_days"] = clean_value(data[3]) if len(data) > 3 else ""

        return Bai2TransactionDetail(
            customer_account=str(customer_account).zfill(10),  # Ensure 10 digits with leading zeros
            currency_code=currency_code,
            transaction_bai_code=transaction_bai_code,
            amount=amount,
            fund_type=fund_type,
            bank_reference=bank_reference,
            customer_reference=customer_reference,
            transaction_text=text,
            fund_available_immediately=funds_data["immediate"],
            fund_available_in_one_day=funds_data["one_day"],
            fund_available_in_two_days=funds_data["two_days"],
        )

    def group_lines_into_transaction(self, lines: List[str]) -> Dict[str, List[str]]:
        """Group lines into transactions."""
        transactions: Dict[str, List[str]] = {}
        current_key = None

        for line in lines:
            data = clean_line(line)
            if not data:
                continue

            if data[0] == self.code:
                current_key = f"{data[1]}_{data[2]}"  # Use type and amount as key
                transactions[current_key] = [line]
            elif data[0] == self.continue_code and current_key:
                transactions[current_key].append(line)

        return transactions

    def get_transaction_lines(self, lines: List[str]) -> List[str]:
        """Get transaction lines from input lines."""
        transaction_lines = []
        found_start = False

        for line in lines:
            data = clean_line(line)
            if not data:
                continue

            if data[0] == self.code:
                found_start = True
                transaction_lines.append(line)
            elif found_start and data[0] in [self.continue_code]:
                transaction_lines.append(line)
            elif found_start and data[0] == self.end_code:
                break

        return transaction_lines

    def get_customer_account(self, line: str) -> Tuple[str, str]:
        """Extract customer account and currency code from line."""
        data = clean_line(line)
        # Format: 03,account,balance,currency
        if len(data) < 4:
            raise ValueError(f"Invalid account identifier record: {line}")

        # Get the currency code from the group header if available
        currency_code = "USD"  # Default to USD if not specified
        for i, field in enumerate(data):
            if field == "USD":
                currency_code = field
                break

        return data[1], currency_code


class BaiFileParser(Bai2SingleModelParser[BaiFileHeaderModel]):
    """Parser for complete BAI2 files."""

    def parse(self, lines: List[str]) -> Optional[BaiFileHeaderModel]:
        """Parse a complete BAI2 file."""
        return self.parse_file_model(lines)

    def group_lines(
        self,
        lines: List[str],
        accepted_codes: List[str],
        initial_code: str,
        break_code: str,
    ) -> Dict[str, List[str]]:
        """Group lines by their codes."""
        groups: Dict[str, List[str]] = {}
        current_group = None

        for line in lines:
            data = clean_line(line)
            if not data:
                continue

            if data[0] == initial_code:
                current_group = data[1]  # Use identifier as group key
                groups[current_group] = [line]
            elif current_group and data[0] in accepted_codes:
                groups[current_group].append(line)
            elif data[0] == break_code:
                break

        return groups

    def split_lines_into_groups(self, lines: List[str]) -> Dict[str, List[str]]:
        """Split lines into group sections."""
        return self.group_lines(
            lines,
            [code.value for code in RecordCode],
            RecordCode.group_header.value,
            RecordCode.file_trailer.value,
        )

    def split_lines_into_accounts(self, lines: List[str]) -> Dict[str, List[str]]:
        """Split lines into account sections."""
        return self.group_lines(
            lines,
            [code.value for code in RecordCode],
            RecordCode.account_identifier.value,
            RecordCode.group_trailer.value,
        )

    def parse_account_models(self, account_lines: List[str]) -> Optional[BaiAccountModel]:
        """Parse account lines into account models."""
        if not account_lines:
            return None

        # Parse transaction summaries
        summary_parser = Bai2TransactionSummaryParser()
        transaction_summaries = summary_parser.parse(account_lines) or []

        # Parse transaction details
        detail_parser = Bai2TransactionDetailParser()
        transaction_details = detail_parser.parse(account_lines) or []

        # Parse account trailer
        trailer_parser = Bai2AccountTrailerParser()
        account_trailer = trailer_parser.parse(account_lines)

        if not account_trailer:
            return None

        return BaiAccountModel(
            transaction_summary=transaction_summaries,
            transaction_detail=transaction_details,
            account_trailer=account_trailer,
        )

    def parse_group_models(self, group_lines: List[str]) -> Optional[BaiGroupModel]:
        """Parse group lines into group models."""
        if not group_lines:
            return None

        # Parse group header
        header_parser = Bai2GroupHeaderParser()
        group_header = header_parser.parse(group_lines)

        # Parse group trailer
        trailer_parser = Bai2GroupTrailerParser()
        group_trailer = trailer_parser.parse(group_lines)

        if not group_header or not group_trailer:
            return None

        # Parse accounts
        account_groups = self.split_lines_into_accounts(group_lines)
        account_models: List[BaiAccountModel] = []
        for account_lines in account_groups.values():
            account_model = self.parse_account_models(account_lines)
            if account_model:
                account_models.append(account_model)

        return BaiGroupModel(
            group_header=group_header,
            group_trailer=group_trailer,
            accounts=account_models,
        )

    def parse_file_model(self, lines: List[str]) -> Optional[BaiFileHeaderModel]:
        """Parse lines into a complete file model."""
        if not lines:
            return None

        # Parse file header
        header_parser = Bai2FileHeaderParser()
        file_header = header_parser.parse(lines)

        # Parse file trailer
        trailer_parser = Bai2FileTrailerParser()
        file_trailer = trailer_parser.parse(lines)

        if not file_header or not file_trailer:
            return None

        # Parse groups
        group_sections = self.split_lines_into_groups(lines)
        group_models: List[BaiGroupModel] = []
        for group_lines in group_sections.values():
            group_model = self.parse_group_models(group_lines)
            if group_model:
                group_models.append(group_model)

        return BaiFileHeaderModel(
            file_header=file_header,
            file_trailer=file_trailer,
            group_headers=group_models,
        )
