#!/usr/bin/env python3
"""Reference solution for find-largest-file task."""

import os
import glob

largest_size = 0
largest_file = None

# Walk through all files recursively
for root, dirs, files in os.walk('.'):
    for file in files:
        filepath = os.path.join(root, file)
        try:
            size = os.path.getsize(filepath)
            if size > largest_size:
                largest_size = size
                largest_file = filepath
        except (OSError, FileNotFoundError):
            pass

# Normalize path (remove leading ./)
if largest_file:
    if largest_file.startswith('./'):
        largest_file = largest_file[2:]
    
    with open('largest.txt', 'w') as f:
        f.write(f"{largest_file} {largest_size}\n")
