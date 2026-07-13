# Extract Emails

## Task

Extract all unique email addresses from the text files in the environment and output them in sorted order.

## Requirements

1. Find and extract all email addresses from files in the environment
2. Remove duplicates
3. Sort alphabetically
4. Write one email per line to `emails.txt`

## Email Format

Valid emails match the basic pattern: `word@word.word`

Examples of valid emails:
- user@example.com
- alice.smith@company.co.uk
- support+tag@domain.org

## Example

If the input files contain:

```
Contact us at support@example.com or help@example.com
Customer: alice@company.org
Support team: support@example.com
```

Then `emails.txt` should contain:

```
alice@company.org
help@example.com
support@example.com
```

## Notes

- Duplicate emails should appear only once in output
- Output must be sorted alphabetically (case-insensitive sort)
- Include all unique emails found across all files
