#!/usr/bin/env python3
"""Reference solution for transform-data-format task."""

import csv
import json
from pathlib import Path


def transform_json_to_csv(json_file: str, csv_file: str) -> None:
    """
    Convert JSON array data to CSV format.
    
    Args:
        json_file: Path to input JSON file
        csv_file: Path to output CSV file
    """
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    if not data or not isinstance(data, list):
        raise ValueError("JSON must contain an array of objects")
    
    # Get field names from first object
    fieldnames = list(data[0].keys())
    
    # Write CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            # Handle missing fields
            row_data = {field: row.get(field, '') for field in fieldnames}
            writer.writerow(row_data)


if __name__ == '__main__':
    transform_json_to_csv('data.json', 'output.csv')
