"""
BAI2 file format models.
This module contains Pydantic models representing the BAI2 file structure.
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecordCode(str, Enum):
    """
    Record codes for BAI2 files as per the specification.
    Each line in the BAI2 file is identified by a record code at the beginning of the line.
    """

    file_header = "01"
    group_header = "02"
    account_identifier = "03"
    transaction_detail = "16"
    account_trailer = "49"
    continuation = "88"
    group_trailer = "98"
    file_trailer = "99"


class MultiLineCodes(str, Enum):
    """Codes that can span multiple lines in a BAI2 file."""

    account_codes = [
        RecordCode.account_identifier,
        RecordCode.account_trailer,
        RecordCode.transaction_detail,
        RecordCode.continuation,
    ]
    group_codes = [RecordCode.group_header, RecordCode.group_trailer]


class ConfiguredBaseModel(BaseModel):
    """Base model with configuration for BAI2 models."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("*", mode="before")
    def convert_numeric_to_string(cls, v):
        """Convert numeric values to strings to preserve leading zeros."""
        if isinstance(v, (int, float)):
            return str(v)
        return v


class Bai2FileHeader(ConfiguredBaseModel):
    """BAI2 file header record (01)."""

    sender_id: str = Field(..., description="Sender identification number")
    receiver_id: str = Field(..., description="Receiver identification number")
    creation_date: str = Field(..., description="File creation date (YYYYMMDD)")
    creation_time: str = Field(..., description="File creation time (HHMM)")
    file_id: str = Field(..., description="File identification number")
    physical_record_length: str = Field("", description="Physical record length")
    block_size: str = Field("", description="Block size")
    version_number: str = Field("2", description="Version number")


class Bai2GroupHeader(ConfiguredBaseModel):
    """BAI2 group header record (02)."""

    receiver_id: str = Field(..., description="Receiver identification number")
    originator_id: str = Field(..., description="Originator identification number")
    group_status: str = Field(..., description="Group status (1=Update)")
    as_of_date: str = Field(..., description="As-of-date (YYYYMMDD)")
    as_of_time: str = Field("", description="As-of-time (HHMM)")
    currency_code: str = Field("", description="Currency code")
    date_type: str = Field("", description="As-of-date modifier")


class Bai2AccountTrailer(ConfiguredBaseModel):
    """BAI2 account trailer record (49)."""

    account_control_total: str = Field(..., description="Account control total")
    number_of_records: str = Field(..., description="Number of records")
    number_of_credits: str = Field("0", description="Number of credits")
    total_credits: str = Field("0", description="Total amount of credits")
    number_of_debits: str = Field("0", description="Number of debits")
    total_debits: str = Field("0", description="Total amount of debits")


class Bai2GroupTrailer(ConfiguredBaseModel):
    """BAI2 group trailer record (98)."""

    group_control_total: str = Field(..., description="Group control total")
    number_of_accounts: str = Field(..., description="Number of accounts")
    number_of_records: str = Field(..., description="Number of records")
    number_of_credits: str = Field("0", description="Number of credits")
    total_credits: str = Field("0", description="Total amount of credits")
    number_of_debits: str = Field("0", description="Number of debits")


class Bai2FileTrailer(ConfiguredBaseModel):
    """BAI2 file trailer record (99)."""

    file_control_total: str = Field(..., description="File control total")
    number_of_groups: str = Field(..., description="Number of groups")
    number_of_records: str = Field(..., description="Number of records")
    number_of_credits: str = Field("0", description="Number of credits")
    total_credits: str = Field("0", description="Total amount of credits")
    number_of_debits: str = Field("0", description="Number of debits")


class Bai2TransactionSummary(ConfiguredBaseModel):
    """BAI2 transaction summary record."""

    customer_account: str = Field(..., description="Customer account number")
    currency_code: str = Field(..., description="Currency code")
    transaction_bai_code: str = Field(..., description="Transaction type code")
    amount: str = Field(..., description="Amount")
    transaction_code: str = Field("", description="Transaction code")
    transaction_type: str = Field("", description="Transaction type")
    fund_available_immediately: Optional[str] = Field(
        None, description="Funds available immediately"
    )
    fund_available_in_one_day: Optional[str] = Field(
        None, description="Funds available in one business day"
    )
    fund_available_in_two_days: Optional[str] = Field(
        None, description="Funds available in two business days"
    )


class Bai2TransactionDetail(ConfiguredBaseModel):
    """BAI2 transaction detail record (16)."""

    customer_account: str = Field(..., description="Customer account number")
    currency_code: str = Field(..., description="Currency code")
    transaction_bai_code: str = Field(..., description="Transaction type code")
    amount: str = Field(..., description="Amount")
    fund_type: str = Field(..., description="Fund type")
    bank_reference: str = Field(..., description="Bank reference number")
    customer_reference: str = Field(..., description="Customer reference number")
    transaction_text: str = Field("", description="Transaction description")
    fund_available_immediately: Optional[str] = Field(
        None, description="Funds available immediately"
    )
    fund_available_in_one_day: Optional[str] = Field(
        None, description="Funds available in one business day"
    )
    fund_available_in_two_days: Optional[str] = Field(
        None, description="Funds available in two business days"
    )


class BaiAccountModel(ConfiguredBaseModel):
    """Model representing a complete BAI2 account section."""

    transaction_summary: List[Bai2TransactionSummary] = Field(default_factory=list)
    transaction_detail: List[Bai2TransactionDetail] = Field(default_factory=list)
    account_trailer: Bai2AccountTrailer


class BaiGroupModel(ConfiguredBaseModel):
    """Model representing a complete BAI2 group section."""

    group_header: Bai2GroupHeader
    group_trailer: Bai2GroupTrailer
    accounts: List[BaiAccountModel] = Field(default_factory=list)


class BaiFileHeaderModel(ConfiguredBaseModel):
    """Model representing a complete BAI2 file."""

    file_header: Bai2FileHeader
    file_trailer: Bai2FileTrailer
    group_headers: List[BaiGroupModel] = Field(default_factory=list)

    def model_transform(
        self,
        model: ConfiguredBaseModel,
        prefix: str,
        index: int = 0,
        add_index: bool = False,
    ) -> Dict[str, str]:
        """Transform a model into a dictionary with prefixed keys."""
        dict_ob = model.model_dump()
        transform_ob = {
            (prefix + key if not key.startswith(prefix) else key): value
            for key, value in dict_ob.items()
        }
        if add_index:
            transform_ob["_index"] = index
        return transform_ob

    def transform_to_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Transform the BAI2 file model into summary and detail DataFrames."""
        transaction_summaries = []
        transaction_details = []
        transformed_file_header = self.model_transform(self.file_header, "file_header_")
        transformed_file_trailer = self.model_transform(self.file_trailer, "file_trailer_")
        for group in self.group_headers:
            transformed_group_header = self.model_transform(group.group_header, "group_header_")
            transformed_group_trailer = self.model_transform(group.group_trailer, "group_trailer_")
            for account in group.accounts:
                transformed_account_trailer = self.model_transform(
                    account.account_trailer, "account_trailer_"
                )
                for idx, summary in enumerate(account.transaction_summary):
                    transaction_summaries.append(
                        transformed_file_header
                        | transformed_group_header
                        | self.model_transform(summary, "", index=idx, add_index=True)
                        | transformed_account_trailer
                        | transformed_group_trailer
                        | transformed_file_trailer
                    )
                for idx, t_detail in enumerate(account.transaction_detail):
                    transaction_details.append(
                        transformed_file_header
                        | transformed_group_header
                        | self.model_transform(t_detail, "", index=idx, add_index=True)
                        | transformed_account_trailer
                        | transformed_group_trailer
                        | transformed_file_trailer
                    )
        return pd.DataFrame(transaction_summaries), pd.DataFrame(transaction_details)
