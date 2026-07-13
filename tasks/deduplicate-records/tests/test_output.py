#!/usr/bin/env python3
"""Test for deduplicate-records task."""

import sys
from pathlib import Path


def test_unique_records():
    """Test that unique.txt contains unique sorted records."""
    
    unique_file = Path("unique.txt")
    
    if not unique_file.exists():
        print("ERROR: unique.txt not found")
        return False
    
    # Read records
    try:
        lines = unique_file.read_text().strip().split('\n')
        lines = [l.strip() for l in lines if l.strip()]
    except Exception as e:
        print(f"ERROR: Could not read unique.txt: {e}")
        return False
    
    # Expected unique records
    expected = ['user111', 'user123', 'user222', 'user456', 'user789']
    
    # Check count
    if len(lines) != len(expected):
        print(f"ERROR: Expected {len(expected)} records, got {len(lines)}")
        print(f"Expected: {expected}")
        print(f"Got: {lines}")
        return False
    
    # Check content
    if lines != expected:
        print(f"ERROR: Records don't match")
        print(f"Expected: {expected}")
        print(f"Got: {lines}")
        return False
    
    # Check for duplicates
    if len(lines) != len(set(lines)):
        print(f"ERROR: Found duplicate records")
        return False
    
    # Check if sorted
    sorted_lines = sorted(lines)
    if lines != sorted_lines:
        print(f"ERROR: Records not sorted")
        return False
    
    print(f"OK: unique.txt contains {len(lines)} unique sorted records")
    return True


if __name__ == "__main__":
    success = test_unique_records()
    sys.exit(0 if success else 1)
