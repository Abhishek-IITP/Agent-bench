#!/usr/bin/env python3
"""Reference solution for sort-json-by-field task."""

import json

# Read the input JSON
with open('data.json', 'r') as f:
    data = json.load(f)

# Sort by name field
sorted_data = sorted(data, key=lambda x: x['name'])

# Write to output file with 2-space indentation
with open('sorted.json', 'w') as f:
    json.dump(sorted_data, f, indent=2)
