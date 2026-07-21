#!/usr/bin/env python3
"""
Broken script that needs to be fixed.
This script has multiple errors:
1. Missing import
2. Syntax error
3. Logic error
4. Wrong output format
"""

# Missing imports - needs to add these

def process_numbers(input_file, output_file):
    numbers = []
    
    # Read numbers from input file
    with open(input_file, 'r') as f:
        for line in f:
            try:
                num = int(line.strip())
                numbers.append(num)
            except ValueError:
                pass  # Skip invalid lines
    
    if not numbers:
        raise ValueError("No valid numbers found in input file")
    
    # Calculate statistics
    total = 0
    for num in numbers:
        total = total + num  # Syntax error here: should be +=
    
    product = 1
    for num in numbers:
        product = product * num
    
    average = total // len(numbers)  # Logic error: should be / not //
    
    # Write results
    with open(output_file, 'w') as f:
        f.write(f"Sum: {total}\n")
        f.write(f"Product: {product}\n")
        f.write(f"Average: {average}\n")  # Wrong format for average


# Missing main block - no error handling
if __name__ == '__main__':
    process_numbers('input.txt', 'result.txt')
