#!/usr/bin/env python3
"""
Evaluation tests for the find-database-files task.

These tests verify that the agent's solution is correct.
"""

import os
import sys


def test_output_file_exists():
    """Test that output.txt was created."""
    output_path = "/workspace/output.txt"
    assert os.path.exists(output_path), f"output.txt not found at {output_path}"
    print("✓ output.txt exists")


def test_output_file_not_empty():
    """Test that output.txt has content."""
    output_path = "/workspace/output.txt"
    assert os.path.getsize(output_path) > 0, "output.txt is empty"
    print("✓ output.txt is not empty")


def test_output_format():
    """Test that output.txt has correct format (one filename per line)."""
    output_path = "/workspace/output.txt"
    
    with open(output_path, 'r') as f:
        lines = f.readlines()
    
    # Remove empty lines
    lines = [line.strip() for line in lines if line.strip()]
    
    # Each line should be a filename, not contain path separators
    for line in lines:
        assert "/" not in line and "\\" not in line, \
            f"Path found in output: {line}"
        assert line, "Empty line found in output"
    
    print(f"✓ Format correct: {len(lines)} filenames")
    return lines


def test_files_are_sorted():
    """Test that filenames are sorted alphabetically."""
    output_path = "/workspace/output.txt"
    
    with open(output_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    sorted_lines = sorted(lines)
    assert lines == sorted_lines, \
        f"Files not sorted. Expected: {sorted_lines}, Got: {lines}"
    
    print("✓ Files are sorted alphabetically")


def test_correct_files_found():
    """Test that the correct files were found."""
    output_path = "/workspace/output.txt"
    
    with open(output_path, 'r') as f:
        found_files = set(line.strip() for line in f.readlines() if line.strip())
    
    # Expected files (those containing "database")
    expected_files = {
        "app_log.txt",           # contains "database"
        "config.json",           # contains "database"
        "deployment_notes.md"    # contains "database"
    }
    
    # Files that should NOT be in the output
    unexpected_files = {
        "notes.txt",     # does NOT contain "database"
        "README.md"      # does NOT contain "database"
    }
    
    # Check all expected files are present
    missing = expected_files - found_files
    assert not missing, f"Missing files that contain 'database': {missing}"
    
    # Check no unexpected files are present
    extras = found_files & unexpected_files
    assert not extras, f"Found files that should NOT contain 'database': {extras}"
    
    # Check total count
    assert len(found_files) == 3, \
        f"Expected 3 files, found {len(found_files)}"
    
    print(f"✓ Correct files found: {sorted(found_files)}")


def main():
    """Run all tests."""
    tests = [
        test_output_file_exists,
        test_output_file_not_empty,
        test_output_format,
        test_files_are_sorted,
        test_correct_files_found,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {len(tests) - failed}/{len(tests)}")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
