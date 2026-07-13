#!/usr/bin/env python3
"""
Test for count-error-lines task.

Validates that count.txt contains the correct count of ERROR lines.
"""

import sys
from pathlib import Path


def test_count_output():
    """Test that count.txt exists and contains the correct count."""
    
    count_file = Path("count.txt")
    
    # Check file exists
    if not count_file.exists():
        print(f"ERROR: count.txt not found")
        return False
    
    # Read the count
    try:
        count_text = count_file.read_text().strip()
        count = int(count_text)
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: Could not read or parse count.txt: {e}")
        return False
    
    # Expected count from app.log (grep shows 3 ERROR lines)
    expected_count = 3
    
    if count != expected_count:
        print(f"ERROR: Expected count {expected_count}, got {count}")
        return False
    
    print(f"OK: count.txt contains correct count: {count}")
    return True


if __name__ == "__main__":
    success = test_count_output()
    sys.exit(0 if success else 1)

