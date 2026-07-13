#!/usr/bin/env python3
"""Test for parse-config-values task."""

import sys
from pathlib import Path


def test_output_values():
    """Test that output.txt contains the correct values."""
    
    output_file = Path("output.txt")
    
    if not output_file.exists():
        print("ERROR: output.txt not found")
        return False
    
    # Read lines
    try:
        lines = output_file.read_text().strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]
    except Exception as e:
        print(f"ERROR: Could not read output.txt: {e}")
        return False
    
    # Expected values
    expected = {
        'api.timeout': '30',
        'database.host': 'localhost',
        'database.port': '5432',
    }
    
    # Parse actual values
    actual = {}
    for line in lines:
        if '=' not in line:
            print(f"ERROR: Invalid format: {line}")
            return False
        key, value = line.split('=', 1)
        actual[key] = value
    
    # Check count
    if len(actual) != len(expected):
        print(f"ERROR: Expected {len(expected)} values, got {len(actual)}")
        return False
    
    # Check values
    for key, value in expected.items():
        if actual.get(key) != value:
            print(f"ERROR: {key}={actual.get(key)}, expected {value}")
            return False
    
    # Check if sorted
    sorted_lines = sorted(lines)
    if lines != sorted_lines:
        print(f"ERROR: Output not sorted")
        print(f"Expected: {sorted_lines}")
        print(f"Got: {lines}")
        return False
    
    print(f"OK: output.txt contains {len(actual)} correct values")
    return True


if __name__ == "__main__":
    success = test_output_values()
    sys.exit(0 if success else 1)
