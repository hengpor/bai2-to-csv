"""Tests for transaction code -> text mapping."""

import json
from pathlib import Path

import pandas as pd
import pytest

from bai2_to_csv import Bai2Converter, load_code_mapping
from bai2_to_csv.mapping import DESCRIPTION_COLUMN, apply_code_mapping, resolve_code_mapping

SAMPLE_BAI = Path(__file__).parent / "data" / "sample.bai"


def write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


class TestLoadJsonMapping:
    def test_loads_object(self, tmp_path: Path) -> None:
        path = write(
            tmp_path / "m.json", json.dumps({"100": "Total Credits", "270": "Total Debits"})
        )
        assert load_code_mapping(path) == {"100": "Total Credits", "270": "Total Debits"}

    def test_accepts_str_path_and_strips_whitespace(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.json", json.dumps({" 100 ": "  Total Credits "}))
        assert load_code_mapping(str(path)) == {"100": "Total Credits"}

    def test_extension_is_case_insensitive(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.JSON", json.dumps({"100": "Total Credits"}))
        assert load_code_mapping(path) == {"100": "Total Credits"}

    def test_empty_object(self, tmp_path: Path) -> None:
        assert load_code_mapping(write(tmp_path / "m.json", "{}")) == {}

    def test_invalid_json(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_code_mapping(write(tmp_path / "m.json", "{not json"))

    def test_top_level_not_object(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="must be an object"):
            load_code_mapping(write(tmp_path / "m.json", '["100", "Total Credits"]'))

    def test_non_string_value(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            load_code_mapping(write(tmp_path / "m.json", '{"100": 5}'))

    def test_empty_code(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="empty transaction code"):
            load_code_mapping(write(tmp_path / "m.json", '{"  ": "Blank"}'))

    def test_duplicate_after_strip_conflicts(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.json", '{"100": "A", " 100": "B"}')
        with pytest.raises(ValueError, match="Conflicting text for transaction code '100'"):
            load_code_mapping(path)


class TestLoadCsvMapping:
    def test_loads_rows(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", "code,text\n100,Total Credits\n270,Total Debits\n")
        assert load_code_mapping(path) == {"100": "Total Credits", "270": "Total Debits"}

    def test_preserves_leading_zeros(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", "code,text\n010,Opening Ledger\n")
        assert load_code_mapping(path) == {"010": "Opening Ledger"}

    def test_header_case_whitespace_and_column_order(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", " Text , CODE ,extra\nTotal Credits, 100 ,ignored\n")
        assert load_code_mapping(path) == {"100": "Total Credits"}

    def test_quoted_text_with_comma(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", 'code,text\n100,"Credits, total"\n')
        assert load_code_mapping(path) == {"100": "Credits, total"}

    def test_skips_blank_rows(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", "code,text\n\n100,Total Credits\n,\n")
        assert load_code_mapping(path) == {"100": "Total Credits"}

    def test_handles_utf8_bom(self, tmp_path: Path) -> None:
        path = tmp_path / "m.csv"
        path.write_bytes("\ufeffcode,text\n100,Total Credits\n".encode("utf-8"))
        assert load_code_mapping(path) == {"100": "Total Credits"}

    def test_header_only(self, tmp_path: Path) -> None:
        assert load_code_mapping(write(tmp_path / "m.csv", "code,text\n")) == {}

    def test_empty_file(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="must have a header row"):
            load_code_mapping(write(tmp_path / "m.csv", ""))

    def test_missing_columns(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="columns 'code' and 'text'"):
            load_code_mapping(write(tmp_path / "m.csv", "code,description\n100,X\n"))

    def test_missing_text_value_becomes_empty(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", "code,text\n100\n")
        assert load_code_mapping(path) == {"100": ""}

    def test_empty_code_with_text(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="empty transaction code"):
            load_code_mapping(write(tmp_path / "m.csv", "code,text\n,Orphan\n"))

    def test_duplicate_same_text_allowed(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.csv", "code,text\n100,A\n100,A\n")
        assert load_code_mapping(path) == {"100": "A"}

    def test_duplicate_conflicting_text(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Conflicting text"):
            load_code_mapping(write(tmp_path / "m.csv", "code,text\n100,A\n100,B\n"))


class TestLoadErrors:
    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Mapping file not found"):
            load_code_mapping(tmp_path / "missing.json")

    def test_unsupported_extension(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="Unsupported mapping file type"):
            load_code_mapping(write(tmp_path / "m.txt", "100=Total"))


class TestResolveCodeMapping:
    def test_none(self) -> None:
        assert resolve_code_mapping(None) is None

    def test_dict_is_copied_and_cleaned(self) -> None:
        source = {" 100 ": " Total Credits "}
        result = resolve_code_mapping(source)
        assert result == {"100": "Total Credits"}
        assert result is not source

    def test_dict_with_non_string_value(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            resolve_code_mapping({"100": 1})  # type: ignore[dict-item]

    def test_dict_with_non_string_code(self) -> None:
        with pytest.raises(ValueError, match="must be a string"):
            resolve_code_mapping({100: "Total"})  # type: ignore[dict-item]

    def test_path(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.json", '{"100": "Total Credits"}')
        assert resolve_code_mapping(path) == {"100": "Total Credits"}
        assert resolve_code_mapping(str(path)) == {"100": "Total Credits"}

    def test_unsupported_type(self) -> None:
        with pytest.raises(TypeError, match="code_mapping must be"):
            resolve_code_mapping(123)  # type: ignore[arg-type]


class TestApplyCodeMapping:
    def test_inserts_column_after_code(self) -> None:
        df = pd.DataFrame({"a": ["x", "y", "z"], "transaction_bai_code": ["100", "999", " 270 "]})
        out = apply_code_mapping(df, {"100": "Credits", "270": "Debits"})
        assert list(out.columns) == ["a", "transaction_bai_code", DESCRIPTION_COLUMN]
        assert out[DESCRIPTION_COLUMN].tolist() == ["Credits", "", "Debits"]

    def test_does_not_mutate_input(self) -> None:
        df = pd.DataFrame({"transaction_bai_code": ["100"]})
        apply_code_mapping(df, {"100": "Credits"})
        assert list(df.columns) == ["transaction_bai_code"]

    def test_overwrites_existing_description_column(self) -> None:
        df = pd.DataFrame({"transaction_bai_code": ["100"], DESCRIPTION_COLUMN: ["old"]})
        out = apply_code_mapping(df, {"100": "Credits"})
        assert out[DESCRIPTION_COLUMN].tolist() == ["Credits"]
        assert list(out.columns).count(DESCRIPTION_COLUMN) == 1

    def test_missing_code_column_returns_unchanged(self) -> None:
        df = pd.DataFrame({"a": ["x"]})
        out = apply_code_mapping(df, {"100": "Credits"})
        assert list(out.columns) == ["a"]

    def test_empty_frame(self) -> None:
        out = apply_code_mapping(pd.DataFrame(), {"100": "Credits"})
        assert out.empty


class TestConverterWithMapping:
    def test_no_mapping_leaves_output_unchanged(self) -> None:
        summary_df, detail_df = Bai2Converter().convert_to_dataframes(SAMPLE_BAI)
        assert DESCRIPTION_COLUMN not in summary_df.columns
        assert DESCRIPTION_COLUMN not in detail_df.columns

    def test_mapping_from_dict(self) -> None:
        converter = Bai2Converter(code_mapping={"100": "Total Credits", "10000": "Check Paid"})
        summary_df, detail_df = converter.convert_to_dataframes(SAMPLE_BAI)

        by_code = dict(zip(summary_df["transaction_bai_code"], summary_df[DESCRIPTION_COLUMN]))
        assert by_code["100"] == "Total Credits"
        assert by_code["010"] == ""
        assert detail_df[DESCRIPTION_COLUMN].tolist() == ["Check Paid"]

    def test_mapping_from_json_file(self, tmp_path: Path) -> None:
        path = write(tmp_path / "m.json", json.dumps({"010": "Opening Ledger"}))
        summary_df, _ = Bai2Converter(code_mapping=path).convert_to_dataframes(SAMPLE_BAI)
        assert summary_df.loc[
            summary_df["transaction_bai_code"] == "010", DESCRIPTION_COLUMN
        ].item() == ("Opening Ledger")

    def test_mapping_from_csv_file_end_to_end(self, tmp_path: Path) -> None:
        mapping = write(tmp_path / "m.csv", "code,text\n270,Total Debits\n10000,Check Paid\n")
        summary_csv, detail_csv = tmp_path / "s.csv", tmp_path / "d.csv"
        Bai2Converter(code_mapping=str(mapping)).convert_file(SAMPLE_BAI, summary_csv, detail_csv)

        summary_df = pd.read_csv(summary_csv, dtype=str, na_filter=False)
        detail_df = pd.read_csv(detail_csv, dtype=str, na_filter=False)
        assert summary_df.loc[
            summary_df["transaction_bai_code"] == "270", DESCRIPTION_COLUMN
        ].item() == ("Total Debits")
        assert detail_df[DESCRIPTION_COLUMN].tolist() == ["Check Paid"]

    def test_bad_mapping_fails_at_construction(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            Bai2Converter(code_mapping=tmp_path / "missing.csv")

    def test_mapping_attribute(self) -> None:
        assert Bai2Converter().code_mapping is None
        assert Bai2Converter(code_mapping={"1": "x"}).code_mapping == {"1": "x"}
