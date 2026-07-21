# Find Security Issues in Code

## Objective
Analyze provided code and identify security vulnerabilities. Generate a structured report listing all issues.

## Input
A Python file named `vulnerable_app.py` containing intentional security vulnerabilities.

## Task
1. Review the code in `vulnerable_app.py`
2. Identify all security issues (OWASP Top 10 or common vulnerabilities)
3. Generate a report in `security_report.txt` listing:
   - Vulnerability name
   - Line number (if applicable)
   - Description
   - Severity (Low/Medium/High)
   - Recommended fix

## Common Security Issues to Look For
- SQL Injection
- Command Injection
- Hardcoded credentials/secrets
- Insecure deserialization
- Path traversal vulnerabilities
- Missing input validation
- Insecure random number generation
- Use of deprecated/unsafe functions
- Missing authentication/authorization
- Exposure of sensitive information

## Report Format
```
SECURITY ISSUES FOUND: X

1. SQL Injection (Line: 15)
   Severity: High
   Description: User input directly concatenated into SQL query
   Recommendation: Use parameterized queries

2. Hardcoded Credentials (Line: 3)
   Severity: High
   Description: Database password hardcoded in source
   Recommendation: Use environment variables

...
```

## Example Vulnerabilities
The code may contain:
- Direct SQL string concatenation with user input
- os.system() with unsanitized user input
- Pickled object deserialization without validation
- Hardcoded API keys or passwords
- No input validation on user-supplied data
- Use of eval() on untrusted input
- File operations without path validation

## Scoring
- Correct identification of security issues: +1 point per issue
- Correct severity assignment: +0.5 points per issue
- Proper recommendation format: +0.5 points per issue
- No false positives: penalty for identifying non-issues
