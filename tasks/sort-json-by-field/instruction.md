# Sort JSON by Field

## Task

Read a JSON file containing an array of objects. Sort the array by the `name` field in ascending alphabetical order and write the result to `sorted.json`.

## Requirements

1. Read the file `data.json` from the environment
2. Parse the JSON array
3. Sort by the `name` field (case-sensitive, alphabetical order)
4. Write the sorted array to `sorted.json` with proper JSON formatting
5. Place `sorted.json` in the current working directory

## Input Format

The input file contains a JSON array of objects with at least a `name` field:

```json
[
  {"id": 3, "name": "Charlie"},
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"}
]
```

## Expected Output

The output should be sorted by the `name` field:

```json
[
  {"id": 1, "name": "Alice"},
  {"id": 2, "name": "Bob"},
  {"id": 3, "name": "Charlie"}
]
```

## Notes

- Sort is case-sensitive
- Maintain all fields in each object
- Output must be valid JSON
- Use 2-space indentation for formatting
