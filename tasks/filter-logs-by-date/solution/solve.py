#!/usr/bin/env python3
"""Reference solution for filter-logs-by-date task."""

from datetime import datetime

start_date = datetime(2024, 1, 15)
end_date = datetime(2024, 1, 20)

filtered_lines = []

with open('app.log', 'r') as f:
    for line in f:
        if not line.strip():
            continue
        try:
            # Parse timestamp from the beginning of the line
            timestamp_str = line[:19]  # YYYY-MM-DD HH:MM:SS
            log_date = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            
            # Check if within range
            if start_date <= log_date <= end_date:
                filtered_lines.append(line.rstrip('\n'))
        except (ValueError, IndexError):
            # Skip lines that don't have valid timestamps
            pass

# Write filtered logs
with open('filtered.log', 'w') as f:
    for line in filtered_lines:
        f.write(line + '\n')
