# Filter Logs by Date

## Task

Extract log entries from `app.log` that fall within the date range 2024-01-15 to 2024-01-20 (inclusive).

## Requirements

1. Read `app.log` from the environment
2. Parse timestamps in format: YYYY-MM-DD HH:MM:SS
3. Filter entries between 2024-01-15 00:00:00 and 2024-01-20 23:59:59 (inclusive)
4. Write filtered entries to `filtered.log` preserving original format

## Log Format

```
2024-01-15 10:23:45 INFO: Application started
2024-01-15 10:23:46 INFO: Initializing database
2024-01-20 15:45:30 ERROR: Connection failed
2024-01-21 08:10:00 WARNING: Maintenance window
```

## Expected Behavior

- Keep only entries with dates in the specified range
- Preserve the exact format of each line
- Output order can match input order

## Notes

- Date range is inclusive on both ends
- Only use the date portion from the timestamp for filtering
- Times don't affect the date boundary check (all times within a date are included)
