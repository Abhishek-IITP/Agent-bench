#!/usr/bin/env python3
"""Test for filter-logs-by-date task."""

import sys
from pathlib import Path


def test_filtered_logs():
    """Test that filtered.log contains correct entries."""
    
    filtered_file = Path("filtered.log")
    
    if not filtered_file.exists():
        print("ERROR: filtered.log not found")
        return False
    
    # Read filtered lines
    try:
        lines = filtered_file.read_text().strip().split('\n')
        lines = [l for l in lines if l.strip()]
    except Exception as e:
        print(f"ERROR: Could not read filtered.log: {e}")
        return False
    
    # Expected lines (from app.log within date range)
    expected_count = 6
    if len(lines) != expected_count:
        print(f"ERROR: Expected {expected_count} lines, got {len(lines)}")
        for i, line in enumerate(lines):
            print(f"  {i}: {line}")
        return False
    
    # Check that lines are from correct date range
    for line in lines:
        if not line.strip():
            continue
        try:
            date_part = line[:10]
            year, month, day = date_part.split('-')
            date_int = int(year + month + day)
            # Should be between 20240115 and 20240120
            if date_int < 20240115 or date_int > 20240120:
                print(f"ERROR: Line outside date range: {line}")
                return False
        except (ValueError, IndexError):
            print(f"ERROR: Invalid date format: {line}")
            return False
    
    # Check that excluded dates are not present
    if any("2024-01-14" in line for line in lines):
        print("ERROR: Found entry from 2024-01-14 (should be excluded)")
        return False
    
    if any("2024-01-21" in line for line in lines):
        print("ERROR: Found entry from 2024-01-21 (should be excluded)")
        return False
    
    print(f"OK: filtered.log contains {len(lines)} correct entries")
    return True


if __name__ == "__main__":
    success = test_filtered_logs()
    sys.exit(0 if success else 1)
