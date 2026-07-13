#!/usr/bin/env python3
"""Reference solution for calculate-statistics task."""

import csv
import json
import statistics
from pathlib import Path


def calculate_statistics(csv_file: str, output_file: str) -> None:
    """
    Calculate statistics from CSV file and save to JSON.
    
    Args:
        csv_file: Path to input CSV file
        output_file: Path to output JSON file
    """
    # Read CSV file
    data = {}
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        # Initialize columns (skip first column which is typically ID)
        numeric_columns = headers[1:] if len(headers) > 1 else []
        for col in numeric_columns:
            data[col] = []
        
        # Parse rows
        for row in reader:
            for col in numeric_columns:
                try:
                    value = float(row[col])
                    data[col].append(value)
                except (ValueError, KeyError):
                    pass
    
    # Calculate statistics
    stats = {}
    for col in numeric_columns:
        values = data[col]
        if values:
            stats[col] = {
                'mean': round(statistics.mean(values), 2),
                'median': round(statistics.median(values), 2),
                'stdev': round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
                'min': round(min(values), 2),
                'max': round(max(values), 2),
            }
    
    # Write JSON output
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)


if __name__ == '__main__':
    calculate_statistics('data.csv', 'stats.json')
