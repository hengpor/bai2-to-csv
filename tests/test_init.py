"""Tests for the BAI2 to CSV package __init__ module."""

import pytest

import bai2_to_csv
from bai2_to_csv import (
    Bai2Converter,
    Bai2TransactionDetail,
    Bai2TransactionSummary,
    BaiFileHeaderModel,
)


class TestPackageImports:
    """Test package-level imports and exports."""

    def test_version_exists(self):
        """Test that the package version is defined."""
        assert hasattr(bai2_to_csv, "__version__")
        assert isinstance(bai2_to_csv.__version__, str)
        assert bai2_to_csv.__version__ == "0.1.0"

    def test_all_exports(self):
        """Test that __all__ contains the expected exports."""
        expected_exports = [
            "Bai2Converter",
            "Bai2TransactionDetail",
            "Bai2TransactionSummary",
            "BaiFileHeaderModel",
        ]

        assert hasattr(bai2_to_csv, "__all__")
        assert bai2_to_csv.__all__ == expected_exports

    def test_bai2_converter_import(self):
        """Test that Bai2Converter can be imported and instantiated."""
        converter = Bai2Converter()
        assert converter is not None
        assert hasattr(converter, "convert_file")
        assert hasattr(converter, "convert_to_dataframes")

    def test_bai2_transaction_detail_import(self):
        """Test that Bai2TransactionDetail can be imported and instantiated."""
        detail = Bai2TransactionDetail(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="10000",
            amount="0525",
            fund_type="10000",
            bank_reference="CHECK",
            customer_reference="123456",
            transaction_text="Test transaction",
            fund_available_immediately=None,
            fund_available_in_one_day=None,
            fund_available_in_two_days=None,
        )
        assert detail is not None
        assert detail.customer_account == "1234567890"
        assert detail.currency_code == "USD"

    def test_bai2_transaction_summary_import(self):
        """Test that Bai2TransactionSummary can be imported and instantiated."""
        summary = Bai2TransactionSummary(
            customer_account="1234567890",
            currency_code="USD",
            transaction_bai_code="100",
            amount="125351",
            transaction_code="1",
            transaction_type="S",
            fund_available_immediately=None,
            fund_available_in_one_day=None,
            fund_available_in_two_days=None,
        )
        assert summary is not None
        assert summary.customer_account == "1234567890"
        assert summary.currency_code == "USD"

    def test_bai_file_header_model_import(self):
        """Test that BaiFileHeaderModel can be imported."""
        # We'll just test that it can be imported, as creating a full instance
        # requires many nested objects
        assert BaiFileHeaderModel is not None
        assert hasattr(BaiFileHeaderModel, "transform_to_dataframes")
        assert hasattr(BaiFileHeaderModel, "model_transform")

    def test_direct_import_from_submodules(self):
        """Test that classes can be imported directly from their submodules."""
        from bai2_to_csv.converter import Bai2Converter as DirectConverter
        from bai2_to_csv.models import (
            Bai2TransactionDetail as DirectDetail,
            Bai2TransactionSummary as DirectSummary,
            BaiFileHeaderModel as DirectModel,
        )

        # Test that direct imports work the same as package-level imports
        assert DirectConverter is Bai2Converter
        assert DirectDetail is Bai2TransactionDetail
        assert DirectSummary is Bai2TransactionSummary
        assert DirectModel is BaiFileHeaderModel

    def test_package_docstring(self):
        """Test that the package has a docstring."""
        assert bai2_to_csv.__doc__ is not None
        assert "BAI2 to CSV converter package" in bai2_to_csv.__doc__