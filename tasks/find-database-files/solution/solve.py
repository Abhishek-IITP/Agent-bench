#!/usr/bin/env python3
"""
Solution for finding files containing 'database'.

This is the reference solution that agents will be compared against.
"""

import os
import glob


def solve():
    """
     ).
    """
    
    # Directory to search
    data_dir = "/workspace/data"
    
    # Find all files in the directory
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
            print(f"Warning: Could not read {filepath}: {e}")
            continue
    
    # Sort alphabetically
    matching_files.sort()
    
    # Write to output file
    output_path = "/workspace/output.txt"
    with open(output_path, 'w') as f:
        for filename in matching_files:
            f.write(filename + "\n")
    
    print(f"Found {len(matching_files)} files containing 'database'")
    print(f"Results written to {output_path}")
    
    return matching_files


if __name__ == "__main__":
    solve()
