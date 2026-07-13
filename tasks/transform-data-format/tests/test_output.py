#!/usr/bin/env python3
"""Test harness for transform-data-format task."""

import csv
from pathlib import Path
import sys


def test_output_csv_exists():
    """Test that output.csv exists."""
    csv_file = Path('output.csv')
    assert csv_file.exists(), "output.csv not found"


def test_csv_readable():
    """Test that output.csv is valid CSV."""
    try:
        with open('output.csv', 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) > 0, "CSV file is empty"
    except Exception as e:
        raise AssertionError(f"Failed to read CSV: {e}")


def test_csv_has_header():
    """Test that CSV has header row."""
    with open('output.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader, None)
    
    assert header is not None, "CSV has no header row"
    assert len(header) > 0, "Header row is empty"


def test_csv_has_correct_headers():
    """Test that CSV has expected headers."""
    with open('output.csv', 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
    
    expected_headers = {'id', 'name', 'email', 'department'}
    assert set(fieldnames) == expected_headers, f"Headers {set(fieldnames)} don't match {expected_headers}"


def test_csv_has_correct_rows():
    """Test that CSV has correct number of rows."""
    with open('output.csv', 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Header + 3 data rows = 4 total
    assert len(rows) == 4, f"Expected 4 rows (header + 3 data), got {len(rows)}"


def test_csv_data_integrity():
    """Test that CSV data matches expected values."""
    with open('output.csv', 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Check first data row
    assert rows[0]['id'] == '1', f"First row ID should be '1', got '{rows[0]['id']}'"
    assert rows[0]['name'] == 'Alice Johnson', f"First row name should be 'Alice Johnson', got '{rows[0]['name']}'"
    
    # Check second data row
    assert rows[1]['id'] == '2', f"Second row ID should be '2', got '{rows[1]['id']}'"
    assert rows[1]['name'] == 'Bob Smith', f"Second row name should be 'Bob Smith', got '{rows[1]['name']}'"


if __name__ == '__main__':
    try:
        test_output_csv_exists()
        test_csv_readable()
        test_csv_has_header()
        test_csv_has_correct_headers()
        test_csv_has_correct_rows()
        test_csv_data_integrity()
        print("All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
