#!/bin/bash
# Reference solution for extract-emails task

# Extract emails using grep, remove filenames, sort unique
grep -h -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' *.txt | \
    sort -u > emails.txt
