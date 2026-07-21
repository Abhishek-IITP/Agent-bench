#!/usr/bin/env python3
"""Vulnerable application with intentional security issues."""

import sqlite3
import os
import pickle
import random

# Issue 1: Hardcoded credentials
DB_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdef"

def query_user(user_id):
    """
    Issue 2: SQL Injection vulnerability
    User input is directly concatenated into SQL query
    """
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Vulnerable: direct string concatenation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    
    return cursor.fetchall()


def execute_command(filename):
    """
    Issue 3: Command Injection vulnerability
    User input is passed directly to os.system()
    """
    # Vulnerable: user input in shell command
    result = os.system(f"cat {filename}")
    return result


def load_data(data_str):
    """
    Issue 4: Insecure deserialization
    pickle.loads() on untrusted input
    """
    # Vulnerable: unpickling untrusted data
    data = pickle.loads(data_str)
    return data


def generate_token():
    """
    Issue 5: Insecure random number generation
    Using random instead of secrets module
    """
    # Vulnerable: random is not cryptographically secure
    token = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    return token


def process_file(file_path):
    """
    Issue 6: Path traversal vulnerability
    No validation of file_path parameter
    """
    # Vulnerable: no path validation
    with open(file_path, 'r') as f:
        return f.read()


def validate_input(user_input):
    """
    Issue 7: Missing input validation
    No sanitization of user input
    """
    # Vulnerable: no validation
    email = user_input.get('email', '')
    age = user_input.get('age', 0)
    
    # Direct use without validation
    return {'email': email, 'age': age}


def log_error(error_msg):
    """
    Issue 8: Exposure of sensitive information
    Error details logged with potentially sensitive data
    """
    # Vulnerable: sensitive info in logs
    import logging
    logging.error(f"Error occurred: {error_msg} - DB Password: {DB_PASSWORD}")


if __name__ == '__main__':
    # Example usage with vulnerabilities
    result = query_user("1 OR 1=1")  # SQL injection
    cmd_result = execute_command("sensitive.txt; rm -rf /")  # Command injection
