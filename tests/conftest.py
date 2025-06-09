"""Shared pytest fixtures and configuration for BAI2 to CSV tests."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_bai2_content():
    """Sample BAI2 file content for testing."""
    return [
        "01,000000610,BOA12345,20250525,1400,000000001,,,2/",
        "02,BOA12345,071000039,20250525,1,,,2/",
        "03,1234567890,USD,10000/",
        "88,100,125351,1,S,125351,0,0/",
        "88,110,0,0,S,0,0,0/",
        "88,270,0525,1,S,0525,0,0/",
        "16,10000,0525,10000,000000000,CHECK,123456/",
        "88,transaction text/",
        "49,10000,0525,0,0,0,1/",
        "98,10000,0525,0,0,0,1/",
        "99,10000,0525,0,0,0,1/",
    ]


@pytest.fixture
def sample_bai2_file(tmp_path, sample_bai2_content):
    """Create a temporary BAI2 file for testing."""
    bai_file = tmp_path / "test.bai"
    with open(bai_file, "w") as f:
        for line in sample_bai2_content:
            f.write(line + "\n")
    return bai_file


@pytest.fixture
def invalid_bai2_content():
    """Invalid BAI2 file content for testing error handling."""
    return [
        "This is not a BAI2 file",
        "Invalid format",
        "No proper record codes",
    ]


@pytest.fixture
def invalid_bai2_file(tmp_path, invalid_bai2_content):
    """Create a temporary invalid BAI2 file for testing."""
    bai_file = tmp_path / "invalid.bai"
    with open(bai_file, "w") as f:
        for line in invalid_bai2_content:
            f.write(line + "\n")
    return bai_file


@pytest.fixture
def empty_bai2_file(tmp_path):
    """Create an empty BAI2 file for testing."""
    bai_file = tmp_path / "empty.bai"
    bai_file.touch()
    return bai_file


@pytest.fixture
def sample_csv_output_paths(tmp_path):
    """Provide paths for CSV output files."""
    return {
        "summary": tmp_path / "summary.csv",
        "detail": tmp_path / "detail.csv",
    }


# Configure pytest to show full diff on assertion failures
def pytest_configure(config):
    """Configure pytest settings."""
    config.option.tb = "short"
    config.option.maxfail = 5
