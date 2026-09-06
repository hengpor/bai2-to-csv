import abc
from typing import Dict, List, Optional, Tuple, TypeVar

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
    MultiLineCodes,
    RecordCode,
)


def _split_line(line: str) -> List[str]:
    """Split a BAI2 record and clean each field.

    Fields may carry the BAI2 end-of-record ``/`` marker and trailing whitespace
    (including line separators). Stripping both here keeps every parser simple.
    """
    return [field.strip().rstrip("/") for field in line.split(",")]


T = TypeVar("T")


def _require(value: Optional[T], record_code: str) -> T:
    """Assert a parser produced a value for a required BAI2 record."""
    if value is None:
        raise ValueError(f"BAI2 record {record_code!r} is missing or unparseable")
    return value


def _parse_account_header(line: str) -> Tuple[str, str]:
    """Extract customer_account and currency_code from an 03 account line."""
    data = _split_line(line)
    return data[1], data[2]


class Bai2ParserBase(abc.ABC):
    """Marker base for BAI2 parsers.

    Concrete subclasses define their own ``parse`` method; the return type
    varies (single model vs. list of models) so no shared signature is enforced.
    """

    code: Optional[str] = None


class Bai2SingleModelParser(Bai2ParserBase, abc.ABC):
    pass


class Bai2MultiLinesModelParser(Bai2ParserBase, abc.ABC):
    code: Optional[str] = None
    continue_code = RecordCode.continuation.value
    end_code: Optional[str] = None


class Bai2FileHeaderParser(Bai2SingleModelParser):
    code = RecordCode.file_header.value

    def parse(self, lines: List[str]) -> Optional[Bai2FileHeader]:
        for line in lines:
            data = _split_line(line)
            if data[0] == self.code:
                return Bai2FileHeader(
                    sender_id=data[1],
                    receiver_id=data[2],
                    creation_date=data[3],
                    creation_time=data[4],
                    file_id=data[5],
                    physical_record_length=data[6],
                    block_size=data[7],
                    version_number=data[8],
                )
        return None


class Bai2FileTrailerParser(Bai2SingleModelParser):
    code = RecordCode.file_trailer.value

    def parse(self, lines: List[str]) -> Optional[Bai2FileTrailer]:
        for line in lines:
            data = _split_line(line)
            if data[0] == self.code:
                return Bai2FileTrailer(
                    file_control_total=data[1],
                    number_of_groups=data[2],
                    number_of_records=data[3],
                )
        return None


class Bai2GroupHeaderParser(Bai2SingleModelParser):
    code = RecordCode.group_header.value

    def parse(self, lines: List[str]) -> Optional[Bai2GroupHeader]:
        for line in lines:
            data = _split_line(line)
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


class Bai2GroupTrailerParser(Bai2SingleModelParser):
    code = RecordCode.group_trailer.value

    def parse(self, lines: List[str]) -> Optional[Bai2GroupTrailer]:
        for line in lines:
            data = _split_line(line)
            if data[0] == self.code:
                return Bai2GroupTrailer(
                    group_control_total=data[1],
                    number_of_accounts=data[2],
                    number_of_records=data[3],
                )
        return None


class Bai2AccountTrailerParser(Bai2SingleModelParser):
    code = RecordCode.account_trailer.value

    def parse(self, lines: List[str]) -> Optional[Bai2AccountTrailer]:
        for line in lines:
            data = _split_line(line)
            if data[0] == self.code:
                return Bai2AccountTrailer(account_control_total=data[1], number_of_records=data[2])
        return None


class Bai2TransactionSummaryParser(Bai2MultiLinesModelParser):
    code = RecordCode.account_identifier.value
    end_code = RecordCode.transaction_detail.value

    def parse(self, lines: List[str]) -> Optional[List[Bai2TransactionSummary]]:
        account_summary_lines = self.get_transaction_summary_lines(lines)
        customer_account, currency_code = _parse_account_header(account_summary_lines[0])
        transaction_summary_details = self.get_transaction_summary_items(account_summary_lines[1:])
        account_summary_objects = []
        for details in transaction_summary_details:
            account_summary_objects.append(
                self.parse_transaction_summary_object(customer_account, currency_code, details)
            )
        return account_summary_objects

    def parse_transaction_summary_object(
        self,
        customer_acc: str,
        currency_code: str,
        details: Dict[str, Optional[str]],
    ) -> Bai2TransactionSummary:
        return Bai2TransactionSummary(
            customer_account=customer_acc,
            currency_code=currency_code,
            transaction_bai_code=_require(details["transaction_bai_code"], "88 (bai_code)"),
            amount=_require(details["amount"], "88 (amount)"),
            transaction_code=_require(details["transaction_code"], "88 (transaction_code)"),
            transaction_type=_require(details["transaction_type"], "88 (transaction_type)"),
            fund_available_immediately=details["fund_available_immediately"],
            fund_available_in_one_day=details["fund_available_in_one_day"],
            fund_available_in_two_days=details["fund_available_in_two_days"],
        )

    def get_transaction_summary_items(self, lines: List[str]) -> List[Dict[str, Optional[str]]]:
        transaction_details: List[Dict[str, Optional[str]]] = []
        for line in lines:
            data = _split_line(line)
            fund_available_immediately = None
            fund_available_in_one_day = None
            fund_available_in_two_days = None
            if len(data) >= 8:
                fund_available_immediately = data[5]
                fund_available_in_one_day = data[6]
                fund_available_in_two_days = data[7]
            transaction_details.append(
                {
                    "transaction_bai_code": data[1],
                    "amount": data[2],
                    "transaction_code": data[3],
                    "transaction_type": data[4],
                    "fund_available_immediately": fund_available_immediately,
                    "fund_available_in_one_day": fund_available_in_one_day,
                    "fund_available_in_two_days": fund_available_in_two_days,
                }
            )
        return transaction_details

    def get_customer_account(self, line: str) -> Tuple[str, str]:
        return _parse_account_header(line)

    def get_transaction_summary_lines(self, lines: List[str]) -> List[str]:
        account_summary_lines = []
        for line in lines:
            data = _split_line(line)
            if data[0] == self.code or data[0] == self.continue_code:
                account_summary_lines.append(line)
            if data[0] == self.end_code:
                break
        return account_summary_lines


class Bai2TransactionDetailParser(Bai2MultiLinesModelParser):
    code = RecordCode.transaction_detail.value
    end_code = RecordCode.account_trailer.value

    def parse(self, lines: List[str]) -> Optional[List[Bai2TransactionDetail]]:
        transaction_lines = self.get_transaction_lines(lines)
        group_lines = self.group_lines_into_transaction(transaction_lines)
        customer_account, currency_code = _parse_account_header(lines[0])
        transaction_obj = []
        for _, group in group_lines.items():
            transaction_obj.append(
                self.parse_group_to_transaction(group, customer_account, currency_code)
            )
        return transaction_obj

    def parse_group_to_transaction(
        self, lines: List[str], customer_account: str, currency_code: str
    ) -> Bai2TransactionDetail:
        texts: List[str] = []
        transaction_bai_code: Optional[str] = None
        amount: Optional[str] = None
        fund_type: Optional[str] = None
        bank_reference: Optional[str] = None
        customer_reference: Optional[str] = None
        fund_available_immediately: Optional[str] = None
        fund_available_in_one_day: Optional[str] = None
        fund_available_in_two_days: Optional[str] = None
        for line in lines:
            data = _split_line(line)
            if data[0] == self.code:
                transaction_bai_code = data[1]
                amount = data[2]
                fund_type = data[3]
                bank_reference = data[-2]
                customer_reference = data[-1]
            if len(data) >= 8:
                fund_available_immediately = data[4]
                fund_available_in_one_day = data[5]
                fund_available_in_two_days = data[6]
            if data[0] == self.continue_code:
                texts.append(data[1].strip())
        transaction_text = "||".join(texts)
        return Bai2TransactionDetail(
            customer_account=customer_account,
            currency_code=currency_code,
            transaction_bai_code=_require(transaction_bai_code, "16 (bai_code)"),
            amount=_require(amount, "16 (amount)"),
            fund_type=_require(fund_type, "16 (fund_type)"),
            bank_reference=_require(bank_reference, "16 (bank_reference)"),
            customer_reference=_require(customer_reference, "16 (customer_reference)"),
            transaction_text=transaction_text,
            fund_available_immediately=fund_available_immediately,
            fund_available_in_one_day=fund_available_in_one_day,
            fund_available_in_two_days=fund_available_in_two_days,
        )

    def group_lines_into_transaction(self, lines: List[str]) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        index = 0
        for line in lines:
            data = _split_line(line)
            if data[0] == self.end_code:
                break
            if data[0] == self.code:
                index += 1
            key = f"key_{index}"
            if key not in groups:
                groups[key] = []
            groups[key].append(line)
        return groups

    def get_transaction_lines(self, lines: List[str]) -> List[str]:
        transaction_lines = []
        is_in_transaction_detail_block = False
        for line in lines:
            data = _split_line(line)
            if data[0] == self.end_code:
                break
            if data[0] == self.code:
                transaction_lines.append(line)
                is_in_transaction_detail_block = True
            if is_in_transaction_detail_block and data[0] == self.continue_code:
                transaction_lines.append(line)
        return transaction_lines


class BaiFileParser(Bai2SingleModelParser):
    def parse(self, lines: List[str]) -> BaiFileHeaderModel:
        return self.parse_file_model(lines)

    def group_lines(
        self,
        lines: List[str],
        accepted_codes: List[str],
        initial_code: str,
        break_code: str,
        key_prefix: str = "group",
    ) -> Dict[str, List[str]]:
        # Skip the enclosing header line (file header for groups, group header for
        # accounts). Every subsequent record whose code is in accepted_codes is
        # attached to the current group; lines outside accepted_codes are skipped,
        # which makes break_code redundant at runtime but kept for API stability.
        del break_code
        groups: Dict[str, List[str]] = {}
        index = -1
        for line in lines[1:]:
            data = _split_line(line)
            if data[0] == initial_code:
                index += 1
            if index < 0 or data[0] not in accepted_codes:
                continue
            key = f"{key_prefix}_{index}"
            groups.setdefault(key, []).append(line)
        return groups

    def split_lines_into_groups(self, lines: List[str]) -> Dict[str, List[str]]:
        accepted_code = MultiLineCodes.group_codes.value + MultiLineCodes.account_codes.value
        return self.group_lines(
            lines,
            accepted_code,
            RecordCode.group_header.value,
            RecordCode.file_trailer.value,
            key_prefix="group",
        )

    def split_lines_into_accounts(self, lines: List[str]) -> Dict[str, List[str]]:
        return self.group_lines(
            lines,
            MultiLineCodes.account_codes.value,
            RecordCode.account_identifier.value,
            RecordCode.group_trailer.value,
            key_prefix="account",
        )

    def parse_account_models(self, account_lines: List[str]) -> BaiAccountModel:
        transaction_summary = Bai2TransactionSummaryParser().parse(account_lines)
        transaction_detail = Bai2TransactionDetailParser().parse(account_lines)
        account_trailer = Bai2AccountTrailerParser().parse(account_lines)
        return BaiAccountModel(
            transaction_summary=_require(transaction_summary, "account transaction summaries"),
            transaction_detail=_require(transaction_detail, "account transaction details"),
            account_trailer=_require(account_trailer, "49 (account trailer)"),
        )

    def parse_group_models(self, group_lines: List[str]) -> BaiGroupModel:
        accounts = []
        for _, account in self.split_lines_into_accounts(group_lines).items():
            accounts.append(self.parse_account_models(account))
        return BaiGroupModel(
            group_header=_require(Bai2GroupHeaderParser().parse(group_lines), "02 (group header)"),
            group_trailer=_require(
                Bai2GroupTrailerParser().parse(group_lines), "98 (group trailer)"
            ),
            accounts=accounts,
        )

    def parse_file_model(self, lines: List[str]) -> BaiFileHeaderModel:
        file_header = _require(Bai2FileHeaderParser().parse(lines), "01 (file header)")
        file_trailer = _require(Bai2FileTrailerParser().parse(lines), "99 (file trailer)")
        groups = []
        for _, group in self.split_lines_into_groups(lines).items():
            groups.append(self.parse_group_models(group))
        return BaiFileHeaderModel(
            file_header=file_header, file_trailer=file_trailer, group_headers=groups
        )
