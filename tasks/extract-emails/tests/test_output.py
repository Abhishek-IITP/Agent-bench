#!/usr/bin/env python3
"""
Test for extract-emails task.

Validates that emails.txt contains all unique emails sorted alphabetically.
"""

import sys
from pathlib import Path


def test_emails_output():
    """Test that emails.txt contains the correct unique sorted emails."""
    
    emails_file = Path("emails.txt")
    
    # Check file exists
    if not emails_file.exists():
        print(f"ERROR: emails.txt not found")
        return False
    
    # Read emails
    try:
        emails = [line.strip() for line in emails_file.read_text().strip().split('\n') if line.strip()]
    except FileNotFoundError as e:
        print(f"ERROR: Could not read emails.txt: {e}")
        return False
    
    # Expected emails (from the environment files)
    expected_emails = [
        'alice@company.org',
        'billing@company.org',
        'bob.smith@example.com',
        'charlie@domain.co.uk',
        'db-support@technical.io',
        'emergency@example.com',
        'manager@company.org',
        'sales@company.org',
        'support@example.com',
        'tech@example.com',
        'web@example.com',
    ]
    
    # Check if we have the correct emails
    if len(emails) != len(expected_emails):
        print(f"ERROR: Expected {len(expected_emails)} emails, got {len(emails)}")
        print(f"Expected: {expected_emails}")
        print(f"Got: {emails}")
        return False
    
    # Check if emails match (case-sensitive)
    if emails != expected_emails:
        print(f"ERROR: Emails don't match")
        print(f"Expected: {expected_emails}")
        print(f"Got: {emails}")
        return False
    
    # Check if sorted
    if emails != sorted(emails):
        print(f"ERROR: Emails not sorted")
        return False
    
    # Check for duplicates
    if len(emails) != len(set(emails)):
        print(f"ERROR: Duplicate emails found")
        return False
    
    print(f"OK: emails.txt contains {len(emails)} unique sorted emails")
    return True


if __name__ == "__main__":
    success = test_emails_output()
    sys.exit(0 if success else 1)
