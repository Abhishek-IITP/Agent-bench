#!/usr/bin/env python3
"""Test harness for calculate-statistics task."""

import json
from pathlib import Path
import sys


def test_stats_file_exists():
    """Test that stats.json exists."""
    stats_file = Path('stats.json')
    assert stats_file.exists(), "stats.json not found"


def test_stats_file_valid_json():
    """Test that stats.json is valid JSON."""
    with open('stats.json', 'r') as f:
        stats = json.load(f)
    assert isinstance(stats, dict), "stats.json must contain a JSON object"


def test_stats_contains_required_columns():
    """Test that stats contain all required columns."""
    with open('stats.json', 'r') as f:
        stats = json.load(f)
    
    required_columns = {'temperature', 'humidity', 'pressure'}
    assert required_columns.issubset(stats.keys()), f"Missing columns: {required_columns - set(stats.keys())}"


def test_stats_structure():
    """Test that each column has required statistics."""
    with open('stats.json', 'r') as f:
        stats = json.load(f)
    
    required_stats = {'mean', 'median', 'stdev', 'min', 'max'}
    
    for col, col_stats in stats.items():
        assert isinstance(col_stats, dict), f"Column {col} stats must be a dict"
        assert required_stats.issubset(col_stats.keys()), \
            f"Column {col} missing stats: {required_stats - set(col_stats.keys())}"


def test_stats_values():
    """Test that statistics values are reasonable."""
    with open('stats.json', 'r') as f:
        stats = json.load(f)
    
    for col, col_stats in stats.items():
        mean = col_stats['mean']
        median = col_stats['median']
        stdev = col_stats['stdev']
        min_val = col_stats['min']
        max_val = col_stats['max']
        
        # Mean should be between min and max
        assert min_val <= mean <= max_val, f"{col}: mean {mean} not between {min_val} and {max_val}"
        
        # Median should be between min and max
        assert min_val <= median <= max_val, f"{col}: median {median} not between {min_val} and {max_val}"
        
        # Stdev should be non-negative
        assert stdev >= 0, f"{col}: stdev {stdev} is negative"


if __name__ == '__main__':
    try:
        test_stats_file_exists()
        test_stats_file_valid_json()
        test_stats_contains_required_columns()
        test_stats_structure()
        test_stats_values()
        print("All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
