#!/usr/bin/env python3
"""Test for merge-csv-files task."""

import csv
import sys
from pathlib import Path


def test_merged_csv():
    """Test that merged.csv is valid and contains all data."""
    
    merged_file = Path("merged.csv")
    
    if not merged_file.exists():
        print("ERROR: merged.csv not found")
        return False
    
    try:
        with open(merged_file, 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            rows = list(reader)
    except Exception as e:
        print(f"ERROR: Could not read merged.csv: {e}")
        return False
    
    # Check headers
    expected_headers = {'id', 'name', 'age', 'email'}
    actual_headers = set(headers)
    if actual_headers != expected_headers:
        print(f"ERROR: Headers mismatch")
        print(f"Expected: {expected_headers}")
        print(f"Got: {actual_headers}")
        return False
    
    # Check row count
    if len(rows) != 7:
        print(f"ERROR: Expected 7 rows, got {len(rows)}")
        return False
    
    # Check data integrity
    ids_present = set(row.get('id', '').strip() for row in rows if row.get('id', '').strip())
    expected_ids = {'1', '2', '3', '4'}
    if ids_present != expected_ids:
        print(f"ERROR: ID mismatch")
        print(f"Expected: {expected_ids}")
        print(f"Got: {ids_present}")
        return False
    
    print(f"OK: merged.csv is valid ({len(headers)} headers, {len(rows)} rows)")
    return True


if __name__ == "__main__":
    success = test_merged_csv()
    sys.exit(0 if success else 1)
