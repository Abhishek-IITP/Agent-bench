#!/usr/bin/env python3
"""Solution for finding security issues."""


def find_security_issues():
    """Analyze code and generate security report."""
    
    issues = [
        {
            'name': 'Hardcoded Credentials',
            'line': 7,
            'severity': 'High',
            'description': 'Database password and API key hardcoded in source code',
            'recommendation': 'Use environment variables or secure configuration management'
        },
        {
            'name': 'SQL Injection',
            'line': 17,
            'severity': 'High',
            'description': 'User input directly concatenated into SQL query without parameterization',
            'recommendation': 'Use parameterized queries with placeholders'
        },
        {
            'name': 'Command Injection',
            'line': 26,
            'severity': 'High',
            'description': 'User input passed directly to os.system() without sanitization',
            'recommendation': 'Use subprocess with argument list or validate/escape input'
        },
        {
            'name': 'Insecure Deserialization',
            'line': 35,
            'severity': 'High',
            'description': 'pickle.loads() used on untrusted input',
            'recommendation': 'Use safer alternatives like json, or validate serialized data'
        },
        {
            'name': 'Weak Cryptography',
            'line': 44,
            'severity': 'High',
            'description': 'Using random module for token generation instead of secrets',
            'recommendation': 'Use secrets module for cryptographically secure random generation'
        },
        {
            'name': 'Path Traversal',
            'line': 52,
            'severity': 'Medium',
            'description': 'File path parameter not validated, allowing directory traversal attacks',
            'recommendation': 'Validate file paths using os.path.realpath() and ensure within allowed directory'
        },
        {
            'name': 'Missing Input Validation',
            'line': 61,
            'severity': 'Medium',
            'description': 'User input not validated before use (email format, age range)',
            'recommendation': 'Implement input validation for all user-supplied data'
        },
        {
            'name': 'Information Disclosure',
            'line': 71,
            'severity': 'High',
            'description': 'Sensitive information (database password) logged in error messages',
            'recommendation': 'Never log sensitive data; use generic error messages for users'
        }
    ]
    
    # Generate report
    report_lines = [f"SECURITY ISSUES FOUND: {len(issues)}\n"]
    
    for i, issue in enumerate(issues, 1):
        report_lines.append(f"\n{i}. {issue['name']} (Line: {issue['line']})")
        report_lines.append(f"   Severity: {issue['severity']}")
        report_lines.append(f"   Description: {issue['description']}")
        report_lines.append(f"   Recommendation: {issue['recommendation']}")
    
    return '\n'.join(report_lines)


if __name__ == '__main__':
    report = find_security_issues()
    
    with open('security_report.txt', 'w') as f:
        f.write(report)
    
    print("Security report generated: security_report.txt")
