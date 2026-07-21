# Merge CSV Files

## Task

Merge all CSV files in the environment into a single CSV file. Include headers from all files and combine all rows.

## Requirements

1. Find all `.csv` files in the current directory
2. Read each CSV file
3. Combine all unique headers
4. Merge all rows from all files
5. Write to `merged.csv`

## Input Format

Multiple CSV files with potentially different columns:

**file1.csv:**
```
id,name
1,Alice
2,Bob
```

**file2.csv:**
```
id,email
1,alice@example.com
3,charlie@example.com
```

## Expected Output

`merged.csv`:
```
id,name,email
1,Alice,
2,Bob,
1,,alice@example.com
3,,charlie@example.com
```

## Notes

- Preserve the order of headers as they appear
- Use empty cells for missing values
- All headers from all files should be included
