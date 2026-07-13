# Count Error Lines in Log File

## Task

Count the number of lines in `app.log` that contain the word "ERROR". Output the count to `count.txt`.

## Requirements

1. Read the file `app.log` from the environment
2. Count all lines that contain the case-sensitive word "ERROR"
3. Write the count as a single number to `count.txt`
4. Place `count.txt` in the current working directory

## Example

If `app.log` contains:

```
INFO: Application started
ERROR: Connection failed
INFO: Retrying...
ERROR: Authentication failed
DEBUG: Cleanup
ERROR: Database unreachable
```

Then `count.txt` should contain:

```
3
```

## Notes

- The word "ERROR" must match exactly (case-sensitive)
- Only count lines where "ERROR" appears
- The output file should contain only the count, nothing else
