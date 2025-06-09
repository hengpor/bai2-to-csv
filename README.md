# BAI2 to CSV Converter

A Python library for converting Bank Administration Institute (BAI2) files to CSV format. This library provides a simple way to parse BAI2 files and convert them into two CSV files: one for transaction summaries and another for transaction details.

## Installation

You can install the package using pip:

```bash
pip install bai2-to-csv
```

## Usage

Here's a simple example of how to use the library:

```python
from bai2_to_csv import Bai2Converter

# Create a converter instance
converter = Bai2Converter()

# Convert a BAI2 file to CSV
converter.convert_file(
    input_path="path/to/your/input.bai2",
    summary_output_path="path/to/summary.csv",
    detail_output_path="path/to/detail.csv"
)
```

The converter will create two CSV files:
1. A transaction summary file containing aggregated transaction information
2. A transaction detail file containing individual transaction records

## Output Format

### Transaction Summary CSV
The summary CSV file includes the following columns:
- customer_account: Account identifier
- currency_code: Currency of the transactions
- transaction_bai_code: BAI transaction type code
- amount: Transaction amount
- transaction_code: Transaction code
- transaction_type: Type of transaction
- fund_available_immediately: Funds available now
- fund_available_in_one_day: Funds available next day
- fund_available_in_two_days: Funds available in two days

### Transaction Detail CSV
The detail CSV file includes:
- customer_account: Account identifier
- currency_code: Currency of the transactions
- transaction_bai_code: BAI transaction type code
- amount: Transaction amount
- fund_type: Type of funds
- bank_reference: Bank reference number
- customer_reference: Customer reference number
- transaction_text: Detailed transaction description

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/bai2-to-csv.git
cd bai2-to-csv

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Publishing

### Prerequisites

Before publishing, make sure you have:

1. **PyPI Account**: Create accounts on [PyPI](https://pypi.org/account/register/) and [Test PyPI](https://test.pypi.org/account/register/)
2. **API Tokens**: Generate API tokens for both PyPI and Test PyPI
3. **GitHub Secrets**: Add the following secrets to your GitHub repository:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI API token

### Local Publishing

To build and test the package locally:

```bash
# Build and test the package
./scripts/build_package.sh

# Publish to Test PyPI (for testing)
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi your-test-pypi-token
poetry publish --repository testpypi

# Publish to PyPI (production)
poetry config pypi-token.pypi your-pypi-token
poetry publish
```

### Automated Publishing

The project includes automated publishing via GitHub Actions:

1. **Test PyPI**: Use the "Publish to PyPI" workflow dispatch to publish to Test PyPI
2. **Production PyPI**: Create a GitHub release to automatically publish to PyPI

#### Creating a Release

1. Update the version in `pyproject.toml`:
   ```bash
   poetry version patch  # or minor, major
   ```

2. Update the `CHANGELOG.md` with the new version

3. Commit and push changes:
   ```bash
   git add .
   git commit -m "Release v0.1.1"
   git push
   ```

4. Create a GitHub release:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Tag version: `v0.1.1`
   - Release title: `v0.1.1`
   - Describe the changes
   - Click "Publish release"

The GitHub Action will automatically build, test, and publish your package to PyPI.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

### Running Tests

The project includes comprehensive unit tests, integration tests, and linting checks.

#### Quick Test Run
```bash
# Run all tests with coverage
python -m pytest tests/ -v --cov=src/bai2_to_csv --cov-report=term-missing

# Run only unit tests
python -m pytest tests/test_*.py -v

# Run only integration tests
python -m pytest tests/test_integration.py -v
```

#### Full CI Test Suite
```bash
# Run the complete test suite (same as CI)
./scripts/run_tests.sh
```

This will run:
- Code formatting checks (black)
- Import sorting checks (isort)
- Linting (flake8)
- Type checking (mypy)
- Unit tests with coverage reporting

#### Test Coverage
After running tests with coverage, you can view:
- Terminal coverage report
- HTML coverage report: `htmlcov/index.html`
- XML coverage report: `coverage.xml`

### GitHub Actions CI

The project uses GitHub Actions for continuous integration. On every push and pull request, the CI will:

1. **Test Matrix**: Run tests on Python 3.9, 3.10, 3.11, and 3.12
2. **Quality Checks**: Format, imports, linting, and type checking
3. **Unit Tests**: Complete test suite with coverage reporting
4. **Integration Tests**: End-to-end workflow testing
5. **Coverage Reporting**: Upload coverage to Codecov
6. **Artifacts**: Store test results and coverage reports

The CI configuration is in `.github/workflows/ci.yml`.