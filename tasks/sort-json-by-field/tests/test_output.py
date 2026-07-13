#!/usr/bin/env python3
"""
Test for sort-json-by-field task.

Validates that sorted.json contains the correctly sorted array.
"""

import json
import sys
from pathlib import Path


def test_sorted_json():
    """Test that sorted.json contains the correctly sorted array."""
    
    sorted_file = Path("sorted.json")
    
    # Check file exists
    if not sorted_file.exists():
        print(f"ERROR: sorted.json not found")
        return False
    
    # Read and parse JSON
    try:
        with open(sorted_file, 'r') as f:
            sorted_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"ERROR: Could not read or parse sorted.json: {e}")
        return False
    
    # Check if it's a list
    if not isinstance(sorted_data, list):
        print(f"ERROR: sorted.json must contain a JSON array")
        return False
    
    # Expected sorted order by name
    expected_order = ["Alice", "Bob", "Charlie", "Diana", "Zack"]
    
    # Extract names from sorted data
    if len(sorted_data) != len(expected_order):
        print(f"ERROR: Expected {len(expected_order)} items, got {len(sorted_data)}")
        return False
    
    actual_names = [item.get('name') for item in sorted_data]
    
    if actual_names != expected_order:
        print(f"ERROR: Names not in correct order")
        print(f"Expected: {expected_order}")
        print(f"Got: {actual_names}")
        return False
    
    print(f"OK: sorted.json contains correctly sorted array")
    return True


if __name__ == "__main__":
    success = test_sorted_json()
    sys.exit(0 if success else 1)
