#!/bin/bash
# Reference solution for count-error-lines task

# Count lines with ERROR and write to output file
grep -c "ERROR" app.log > count.txt
