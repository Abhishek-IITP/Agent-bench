#!/usr/bin/env python3
"""Test harness for find-security-issues task."""

from pathlib import Path
import sys


def test_report_file_exists():
    """Test that security_report.txt exists."""
    report_file = Path('security_report.txt')
    assert report_file.exists(), "security_report.txt not found"


def test_report_readable():
    """Test that report is readable."""
    try:
        with open('security_report.txt', 'r') as f:
            content = f.read()
        assert len(content) > 0, "Report is empty"
    except Exception as e:
        raise AssertionError(f"Failed to read report: {e}")


def test_report_has_issues_header():
    """Test that report has issues count header."""
    with open('security_report.txt', 'r') as f:
        content = f.read()
    
    assert 'SECURITY ISSUES FOUND:' in content, "Missing 'SECURITY ISSUES FOUND:' header"
    
    # Extract number
    for line in content.split('\n'):
        if 'SECURITY ISSUES FOUND:' in line:
            count_str = line.split(':')[1].strip()
            count = int(count_str)
            assert count >= 5, f"Should find at least 5 security issues, found {count}"


def test_report_identifies_sql_injection():
    """Test that SQL injection is identified."""
    with open('security_report.txt', 'r') as f:
        content = f.read()
    
    assert 'SQL Injection' in content or 'sql' in content.lower(), \
        "SQL Injection vulnerability not identified"


def test_report_identifies_command_injection():
    """Test that command injection is identified."""
    with open('security_report.txt', 'r') as f:
        content = f.read()
    
    assert 'Command Injection' in content or 'command' in content.lower(), \
        "Command Injection vulnerability not identified"


def test_report_identifies_hardcoded_credentials():
    """Test that hardcoded credentials are identified."""
    with open('security_report.txt', 'r') as f:
        content = f.read()
    
    assert 'Hardcoded' in content or 'credentials' in content.lower() or 'password' in content.lower(), \
        "Hardcoded credentials vulnerability not identified"


def test_report_has_severity_levels():
    """Test that report includes severity levels."""
    with open('security_report.txt', 'r') as f:
        content = f.read()
    
    assert 'Severity:' in content, "Severity levels not included in report"
    assert 'High' in content or 'Medium' in content, "No severity information found"


def test_report_has_recommendations():
    """Test that report includes recommendations."""
    with open('security_report.txt', 'r') as f:
        content = f.read()
    
    assert 'Recommendation' in content or 'recommendation' in content.lower(), \
        "Recommendations not included in report"


if __name__ == '__main__':
    try:
        test_report_file_exists()
        test_report_readable()
        test_report_has_issues_header()
        test_report_identifies_sql_injection()
        test_report_identifies_command_injection()
        test_report_identifies_hardcoded_credentials()
        test_report_has_severity_levels()
        test_report_has_recommendations()
        print("All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
