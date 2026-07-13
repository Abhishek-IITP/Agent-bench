# Find Largest File

## Task

Find the largest file in the current directory and all subdirectories. Output the relative file path and size in bytes to `largest.txt`.

## Requirements

1. Search recursively through the current directory and all subdirectories
2. Find the file with the maximum size (in bytes)
3. Output format: `relative/path/to/file.txt SIZE_IN_BYTES`
4. Write to `largest.txt` in the current working directory

## Example

If the largest file is `data/archive.zip` with 1048576 bytes, then `largest.txt` should contain:

```
data/archive.zip 1048576
```

## Notes

- Only files (not directories)
- Size in bytes (not KB, MB)
- Use relative paths from the current directory
- If multiple files have the same size, return any one
