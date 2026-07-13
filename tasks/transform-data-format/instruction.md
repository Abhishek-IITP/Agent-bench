# Transform Data Format (JSON to CSV)

## Objective
Convert JSON array data to CSV format with proper header row and field escaping.

## Input
A JSON file named `data.json` containing an array of objects:
```json
[
  {"name": "Alice", "age": 30, "city": "New York"},
  {"name": "Bob", "age": 25, "city": "San Francisco"},
  ...
]
```

## Task
1. Read the `data.json` file
2. Extract field names from the first object as CSV headers
3. Convert each object to a CSV row
4. Handle special characters and escaping properly
5. Save to `output.csv`

## Requirements
- CSV header row with all field names from the first object
- Proper CSV escaping (quotes around fields with commas, newlines, or quotes)
- Fields should be in the same order as they appear in the first JSON object
- Each row corresponds to one JSON object
- Output must be valid CSV format

## Example Input (data.json)
```json
[
  {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "department": "Engineering"
  },
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob@example.com",
    "department": "Sales"
  },
  {
    "id": 3,
    "name": "Carol White",
    "email": "carol@example.com",
    "department": "HR"
  }
]
```

## Expected Output (output.csv)
```csv
id,name,email,department
1,Alice Johnson,alice@example.com,Engineering
2,Bob Smith,bob@example.com,Sales
3,Carol White,carol@example.com,HR
```

## Edge Cases
- Fields containing commas should be quoted
- Fields containing quotes should have quotes escaped and be quoted
- Fields with newlines should be quoted
- Empty fields should be handled properly
- Fields should be trimmed of leading/trailing whitespace
