# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-XX

### Added
- Initial release of BAI2 to CSV converter
- Support for parsing BAI2 files and converting to CSV format
- Two output formats: transaction summaries and detailed transactions
- Comprehensive test suite with 97% coverage
- Type hints and mypy support
- Pydantic models for data validation
- Support for Python 3.9-3.12
- Automated CI/CD pipeline with GitHub Actions

### Features
- `Bai2Converter` class for file conversion
- Support for both file paths and Path objects
- Robust error handling and validation
- Preservation of data types and formatting
- Integration with pandas for DataFrame output

### Documentation
- Comprehensive README with usage examples
- API documentation through type hints
- Development setup instructions
- Testing guidelines

[Unreleased]: https://github.com/yourusername/bai2-to-csv/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/bai2-to-csv/releases/tag/v0.1.0