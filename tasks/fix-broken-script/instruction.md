# Fix Broken Python Script

## Objective
Debug and fix a broken Python script that has multiple errors. The script should process input data and produce correct results.

## Problem
A Python script named `process_data.py` is broken with:
- Syntax errors
- Logic bugs
- Runtime errors
- Incorrect output format

## Task
1. Analyze the broken script
2. Identify and fix all errors
3. The script should read `input.txt` containing a list of numbers
4. Calculate the sum, product, and average
5. Write results to `result.txt` in the exact format

## Input File (input.txt)
Contains one number per line:
```
5
10
3
8
```

## Expected Output (result.txt)
```
Sum: 26
Product: 1200
Average: 6.5
```

## Script Purpose
The script should:
1. Read all numbers from `input.txt`
2. Calculate sum of all numbers
3. Calculate product of all numbers
4. Calculate average (mean) of all numbers
5. Write results to `result.txt` with proper formatting

## Common Issues to Look For
- Missing imports
- Syntax errors (missing colons, parentheses)
- Incorrect indentation
- Off-by-one errors
- Wrong operators
- Incorrect string formatting
- Missing or incorrect variable initialization
- Division by zero
- File I/O errors

## Hints
- Check the format of output carefully
- Ensure all imports are present
- Verify variable names and types
- Check calculation logic
