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

## License

This project is licensed under the MIT License - see the LICENSE file for details.