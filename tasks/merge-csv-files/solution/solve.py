#!/usr/bin/env python3
"""Reference solution for merge-csv-files task."""

import csv
import glob
from collections import OrderedDict

# Collect all data
all_headers = OrderedDict()
all_rows = []

# Process each CSV file
csv_files = sorted(glob.glob('*.csv'))
for filename in csv_files:
    if filename == 'merged.csv':
        continue
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_rows.append(row)
            for header in reader.fieldnames:
                all_headers[header] = True

# Get the final ordered headers
headers = list(all_headers.keys())

# Write merged CSV
with open('merged.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    writer.writerows(all_rows)
