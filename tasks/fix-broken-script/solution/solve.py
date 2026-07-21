#!/usr/bin/env python3
"""Fixed version of the broken script."""


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
        total += num  # Fixed: use += operator
    
    product = 1
    for num in numbers:
        product *= num  # Fixed: use *= operator
    
    average = total / len(numbers)  # Fixed: use / for float division
    
    # Write results
    with open(output_file, 'w') as f:
        f.write(f"Sum: {total}\n")
        f.write(f"Product: {product}\n")
        f.write(f"Average: {average}\n")


if __name__ == '__main__':
    process_numbers('input.txt', 'result.txt')
