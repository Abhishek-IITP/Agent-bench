# Parse Config Values

## Task

Parse a configuration file and extract specific values in the format `KEY=VALUE`.

## Requirements

1. Read `config.ini` from the environment
2. Extract the values for: `database.host`, `database.port`, `api.timeout`
3. Output to `output.txt` in format: `KEY=VALUE` (one per line)
4. Lines must be sorted alphabetically by KEY

## Config Format

```ini
[database]
host = localhost
port = 5432
user = admin

[api]
timeout = 30
retries = 3
```

## Expected Output

```
api.timeout=30
database.host=localhost
database.port=5432
```

## Notes

- Extract dotted key names (section.key)
- Values may have whitespace around the `=` sign
- Sort output alphabetically
- Only output the three specified keys
