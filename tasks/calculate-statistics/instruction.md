# Calculate Statistics from CSV Data

## Objective
Parse a CSV file containing numeric data and calculate basic statistics. Save the results to a JSON file.

## Input
A CSV file named `data.csv` with a header row and multiple numeric columns:
- Each row represents a record
- Columns contain numeric values
- First column is typically an ID

## Task
1. Read the `data.csv` file
2. For each numeric column (excluding ID), calculate:
   - Mean (average)
   - Median (middle value)
   - Standard deviation
   - Minimum value
   - Maximum value
3. Save results to `stats.json` with format:
```json
{
  "column_name": {
    "mean": float,
    "median": float,
    "stdev": float,
    "min": float,
    "max": float
  },
  ...
}
```

## Example Input (data.csv)
```
id,temperature,humidity,pressure
1,22.5,45.2,1013.2
2,23.1,46.8,1012.9
3,21.8,44.1,1013.5
```

## Expected Output (stats.json)
```json
{
  "temperature": {
    "mean": 22.47,
    "median": 22.5,
    "stdev": 0.58,
    "min": 21.8,
    "max": 23.1
  },
  "humidity": {
    "mean": 45.37,
    "median": 45.2,
    "stdev": 1.35,
    "min": 44.1,
    "max": 46.8
  },
  "pressure": {
    "mean": 1013.2,
    "median": 1013.2,
    "stdev": 0.27,
    "min": 1012.9,
    "max": 1013.5
  }
}
```

## Notes
- Round statistics to 2 decimal places
- Output must be valid JSON
- Must exclude the ID column from statistics
- Handle any number of numeric columns
