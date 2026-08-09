#!/usr/bin/env python3
"""
Solution for finding files containing 'database'.

This is the reference solution that agents will be compared against.
"""

import os
import glob


def solve():
    """Find files in the current environment containing 'database' and output names."""
    
    # Use current directory
    data_dir = "."
    
    # Find all files in the directory (non-recursive, current directory only)
    all_files = glob.glob(os.path.join(data_dir, "*"))
    
    # Filter for files only (not directories)
    files = [f for f in all_files if os.path.isfile(f)]
    
    # Find files containing "database" (case-insensitive)
    matching_files = []
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'database' in content.lower():
                    # Get just the filename, no directory path
                    filename = os.path.basename(filepath)
                    matching_files.append(filename)
        except Exception as e:
            # Skip files that can't be read
            pass
    
    # Sort alphabetically
    matching_files.sort()
    
    # Write to output file (relative path in current directory)
    output_path = "output.txt"
    with open(output_path, 'w') as f:
        for filename in matching_files:
            f.write(filename + "\n")


if __name__ == "__main__":
    solve()
