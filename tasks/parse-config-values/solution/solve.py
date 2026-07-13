#!/usr/bin/env python3
"""Reference solution for parse-config-values task."""

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Extract the required values
required_keys = [
    ('database', 'host'),
    ('database', 'port'),
    ('api', 'timeout'),
]

results = []
for section, key in required_keys:
    value = config.get(section, key)
    results.append(f"{section}.{key}={value}")

# Sort alphabetically
results.sort()

# Write to output
with open('output.txt', 'w') as f:
    for line in results:
        f.write(line + '\n')
