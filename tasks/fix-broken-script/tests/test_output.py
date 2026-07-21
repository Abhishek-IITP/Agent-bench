#!/usr/bin/env python3
"""Test harness for fix-broken-script task."""

from pathlib import Path
import sys


def test_result_file_exists():
    """Test that result.txt exists."""
    result_file = Path('result.txt')
    assert result_file.exists(), "result.txt not found"


def test_result_file_readable():
    """Test that result.txt is readable."""
    try:
        with open('result.txt', 'r') as f:
            content = f.read()
        assert len(content) > 0, "result.txt is empty"
    except Exception as e:
        raise AssertionError(f"Failed to read result.txt: {e}")


def test_result_format():
    """Test that result.txt has correct format."""
    with open('result.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
    
    # Check for expected format
    assert lines[0].startswith('Sum:'), f"First line should start with 'Sum:', got '{lines[0]}'"
    assert lines[1].startswith('Product:'), f"Second line should start with 'Product:', got '{lines[1]}'"
    assert lines[2].startswith('Average:'), f"Third line should start with 'Average:', got '{lines[2]}'"


def test_result_values():
    """Test that calculations are correct."""
    with open('result.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    # Parse values
    sum_value = int(lines[0].split(':')[1].strip())
    product_value = int(lines[1].split(':')[1].strip())
    average_value = float(lines[2].split(':')[1].strip())
    
    # Expected: numbers are 5, 10, 3, 8
    assert sum_value == 26, f"Sum should be 26, got {sum_value}"
    assert product_value == 1200, f"Product should be 1200, got {product_value}"
    assert average_value == 6.5, f"Average should be 6.5, got {average_value}"


def test_no_syntax_errors():
    """Test that script can be imported without syntax errors."""
    try:
        with open('process_data.py', 'r') as f:
            code = f.read()
        compile(code, 'process_data.py', 'exec')
    except SyntaxError as e:
        raise AssertionError(f"Script has syntax errors: {e}")


if __name__ == '__main__':
    try:
        test_result_file_exists()
        test_result_file_readable()
        test_result_format()
        test_result_values()
        test_no_syntax_errors()
        print("All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
