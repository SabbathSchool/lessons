#!/bin/bash

# Check if a file argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <filename>"
    exit 1
fi

FILE=$1

# Perform replacements using sed
sed -i -E "
    s/April 1, 1905/April 5, 2025/g;
    s/April 8, 1905/April 12, 2025/g;
    s/April 15, 1905/April 19, 2025/g;
    s/April 22, 1905/April 26, 2025/g;
    s/April 29, 1905/May 3, 2025/g;
    s/May 6, 1905/May 10, 2025/g;
    s/May 13, 1905/May 17, 2025/g;
    s/May 20, 1905/May 24, 2025/g;
    s/May 27, 1905/May 31, 2025/g;
    s/June 3, 1905/June 7, 2025/g;
    s/June 10, 1905/June 14, 2025/g;
    s/June 17, 1905/June 21, 2025/g;
    s/June 24, 1905/June 28, 2025/g;
" "$FILE"

echo "Date replacements completed in $FILE."
