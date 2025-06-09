from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
from pydantic import BaseModel


class RecordCode(Enum):
    """
    Record codes for BAI2 files as per the specification:
    https://developer.gs.com/docs/services/transaction-banking/bai-file/
    Each line in the BAI2 file is identified by a record code which is located at beginning of the line.
    """

    file_header = "01"
    group_header = "02"
    account_identifier = "03"
    transaction_detail = "16"
    account_trailer = "49"
    continuation = "88"
    group_trailer = "98"
    file_trailer = "99"


class MultiLineCodes(Enum):
    account_codes = [
        RecordCode.account_identifier.value,
        RecordCode.account_trailer.value,
        RecordCode.transaction_detail.value,
        RecordCode.continuation.value,
    ]
    group_codes = [RecordCode.group_header.value, RecordCode.group_trailer.value]


class ConfiguredBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True


class Bai2FileHeader(ConfiguredBaseModel):
    sender_id: str
    receiver_id: str
    creation_date: str
    creation_time: str
    file_id: str
    physical_record_length: str
    block_size: str
    version_number: str = "2"  # BoA version


class Bai2GroupHeader(ConfiguredBaseModel):
    receiver_id: str
    originator_id: str
    group_status: str
    as_of_date: str
    as_of_time: str
    currency_code: str
    date_type: str


class Bai2AccountTrailer(ConfiguredBaseModel):
    account_control_total: str
    number_of_records: str


class Bai2GroupTrailer(ConfiguredBaseModel):
    group_control_total: str
    number_of_accounts: str
    number_of_records: str


class Bai2FileTrailer(ConfiguredBaseModel):
    file_control_total: str
    number_of_groups: str
    number_of_records: str


class Bai2TransactionSummary(ConfiguredBaseModel):
    customer_account: str
    currency_code: str
    transaction_bai_code: str
    amount: str
    transaction_code: str
    transaction_type: str
    fund_available_immediately: Optional[str]
    fund_available_in_one_day: Optional[str]
    fund_available_in_two_days: Optional[str]


class Bai2TransactionDetail(ConfiguredBaseModel):
    customer_account: str
    currency_code: str
    transaction_bai_code: str
    amount: str
    fund_type: str
    bank_reference: str
    customer_reference: str
    transaction_text: str
    fund_available_immediately: Optional[str]
    fund_available_in_one_day: Optional[str]
    fund_available_in_two_days: Optional[str]


class BaiAccountModel(ConfiguredBaseModel):
    transaction_summary: List[Bai2TransactionSummary]
    transaction_detail: List[Bai2TransactionDetail]
    account_trailer: Bai2AccountTrailer


class BaiGroupModel(ConfiguredBaseModel):
    group_header: Bai2GroupHeader
    group_trailer: Bai2GroupTrailer
    accounts: List[BaiAccountModel]


class BaiFileHeaderModel(ConfiguredBaseModel):
    file_header: Bai2FileHeader
    file_trailer: Bai2FileTrailer
    group_headers: List[BaiGroupModel]

    def model_transform(
        self,
        model: ConfiguredBaseModel,
        prefix: str,
        index: int = 0,
        add_index: bool = False,
    ) -> Dict[str, str]:
        dict_ob = model.dict()
        transform_ob = {
            (prefix + key if not key.startswith(prefix) else key): value
            for key, value in dict_ob.items()
        }
        if add_index:
            transform_ob["_index"] = index
        return transform_ob

    def transform_to_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        transaction_summaries = []
        transaction_details = []
        transformed_file_header = self.model_transform(self.file_header, "file_header_")
        transformed_file_trailer = self.model_transform(
            self.file_trailer, "file_trailer_"
        )
        for group in self.group_headers:
            transformed_group_header = self.model_transform(
                group.group_header, "group_header_"
            )
            transformed_group_trailer = self.model_transform(
                group.group_trailer, "group_trailer_"
            )
            for account in group.accounts:
                transformed_account_trailer = self.model_transform(
                    group.group_trailer, "account_trailer_"
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
                for t_detail in account.transaction_detail:
                    transaction_details.append(
                        transformed_file_header
                        | transformed_group_header
                        | self.model_transform(t_detail, "", index=idx, add_index=True)
                        | transformed_account_trailer
                        | transformed_group_trailer
                        | transformed_file_trailer
                    )
        return pd.DataFrame(transaction_summaries), pd.DataFrame(transaction_details)
