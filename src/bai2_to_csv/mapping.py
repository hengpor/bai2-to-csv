"""
Transaction code to text mapping.

Load a mapping of BAI2 transaction codes (``transaction_bai_code``) to
human-readable text from a CSV or JSON file, and apply it to converted frames.

Supported formats:

* JSON: a single object, ``{"100": "Total Credits", "270": "Total Debits"}``
* CSV: a header row with ``code`` and ``text`` columns (any order, case
  insensitive; extra columns are ignored)::

      code,text
      100,Total Credits
      270,Total Debits

Codes are compared as strings, so leading zeros matter (``"010"`` != ``"10"``).
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple, Union

import pandas as pd

CodeMapping = Dict[str, str]
CodeMappingSource = Union[str, Path, Mapping[str, str]]

CODE_COLUMN = "transaction_bai_code"
DESCRIPTION_COLUMN = "transaction_description"

_CSV_CODE_HEADER = "code"
_CSV_TEXT_HEADER = "text"


def _build_mapping(pairs: Iterable[Tuple[Any, Any]], source: str) -> CodeMapping:
    """Validate and clean (code, text) pairs into a mapping."""
    mapping: CodeMapping = {}
    for raw_code, raw_text in pairs:
        if not isinstance(raw_code, str):
            raise ValueError(f"{source}: transaction code {raw_code!r} must be a string")
        if not isinstance(raw_text, str):
            raise ValueError(f"{source}: text for transaction code {raw_code!r} must be a string")
        code, text = raw_code.strip(), raw_text.strip()
        if not code:
            raise ValueError(f"{source}: empty transaction code (text {text!r})")
        if code in mapping and mapping[code] != text:
            raise ValueError(
                f"{source}: Conflicting text for transaction code {code!r}: "
                f"{mapping[code]!r} vs {text!r}"
            )
        mapping[code] = text
    return mapping


def _load_json(path: Path) -> CodeMapping:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in mapping file {path}: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"{path}: JSON mapping must be an object of code -> text")
    return _build_mapping(data.items(), str(path))


def _load_csv(path: Path) -> CodeMapping:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError(f"{path}: CSV mapping must have a header row")
        columns = [name.strip().lower() for name in header]
        if _CSV_CODE_HEADER not in columns or _CSV_TEXT_HEADER not in columns:
            raise ValueError(
                f"{path}: CSV mapping must have columns "
                f"'{_CSV_CODE_HEADER}' and '{_CSV_TEXT_HEADER}', got {header}"
            )
        code_idx = columns.index(_CSV_CODE_HEADER)
        text_idx = columns.index(_CSV_TEXT_HEADER)

        def pairs() -> Iterable[Tuple[str, str]]:
            for row in reader:
                code = row[code_idx] if code_idx < len(row) else ""
                text = row[text_idx] if text_idx < len(row) else ""
                if not code.strip() and not text.strip():
                    continue  # blank row
                yield code, text

        return _build_mapping(pairs(), str(path))


def load_code_mapping(path: Union[str, Path]) -> CodeMapping:
    """
    Load a transaction code -> text mapping from a ``.csv`` or ``.json`` file.

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file type is unsupported or its content is invalid
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Mapping file not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json(path)
    if suffix == ".csv":
        return _load_csv(path)
    raise ValueError(f"Unsupported mapping file type {path.suffix!r}: expected .csv or .json")


def resolve_code_mapping(source: Optional[CodeMappingSource]) -> Optional[CodeMapping]:
    """Turn a file path or an in-memory mapping into a validated mapping."""
    if source is None:
        return None
    if isinstance(source, (str, Path)):
        return load_code_mapping(source)
    if isinstance(source, Mapping):
        return _build_mapping(source.items(), "code_mapping")
    raise TypeError(f"code_mapping must be a file path or a mapping, got {type(source).__name__}")


def apply_code_mapping(df: pd.DataFrame, mapping: Mapping[str, str]) -> pd.DataFrame:
    """
    Return a copy of ``df`` with a ``transaction_description`` column inserted
    right after ``transaction_bai_code``. Unmapped codes get an empty string.
    Frames without a ``transaction_bai_code`` column are returned unchanged.
    """
    if CODE_COLUMN not in df.columns:
        return df
    out = df.drop(columns=[DESCRIPTION_COLUMN], errors="ignore")
    descriptions = out[CODE_COLUMN].astype(str).str.strip().map(mapping).fillna("")
    out.insert(out.columns.get_loc(CODE_COLUMN) + 1, DESCRIPTION_COLUMN, descriptions)
    return out
