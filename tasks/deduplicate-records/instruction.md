# Deduplicate Records

## Task

Remove duplicate lines from `records.txt` and output unique lines in sorted order.

## Requirements

1. Read `records.txt` from the environment
2. Remove duplicate lines
3. Sort remaining lines alphabetically
4. Output to `unique.txt`

## Input Format

File with potentially duplicate entries:

```
apple
banana
apple
cherry
banana
date
apple
```

## Expected Output

```
apple
banana
cherry
date
```

## Notes

- Case-sensitive comparison
- Sort alphabetically
- Preserve the content exactly as-is (just remove duplicates and sort)
