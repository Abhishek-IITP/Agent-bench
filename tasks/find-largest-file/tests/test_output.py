#!/usr/bin/env python3
"""Test for find-largest-file task."""

import sys
import os
from pathlib import Path


def test_largest_file():
    """Test that largest.txt contains the correct file and size."""
    
    largest_file = Path("largest.txt")
    
    if not largest_file.exists():
        print("ERROR: largest.txt not found")
        return False
    
    try:
        content = largest_file.read_text().strip()
        parts = content.split()
        if len(parts) != 2:
            print(f"ERROR: Expected 'path size' format, got: {content}")
            return False
        
        filepath = parts[0]
        size_str = parts[1]
        size = int(size_str)
    except (ValueError, IndexError) as e:
        print(f"ERROR: Could not parse largest.txt: {e}")
        return False
    
    # Check the file exists
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return False
    
    # Check the size
    actual_size = os.path.getsize(filepath)
    if actual_size != size:
        print(f"ERROR: Size mismatch for {filepath}: expected {size}, got {actual_size}")
        return False
    
    # Verify it's actually the largest
    all_files_with_sizes = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            fpath = os.path.join(root, file)
            if fpath.startswith('./'):
                fpath = fpath[2:]
            if fpath != 'largest.txt':
                try:
                    fsize = os.path.getsize(os.path.join(root, file))
                    all_files_with_sizes.append((fpath, fsize))
                except:
                    pass
    
    if all_files_with_sizes:
        max_size = max(s for _, s in all_files_with_sizes)
        if size < max_size:
            print(f"ERROR: {filepath} is not the largest file (size {size} < {max_size})")
            return False
    
    print(f"OK: largest.txt correct ({filepath}: {size} bytes)")
    return True


if __name__ == "__main__":
    success = test_largest_file()
    sys.exit(0 if success else 1)
