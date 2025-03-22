#!/bin/bash

# Function to convert Roman numerals to Arabic
roman_to_arabic() {
    local roman="$1"
    local result=0
    local prev=0
    local value=0
    
    # Convert to uppercase for consistency
    roman=$(echo "$roman" | tr '[:lower:]' '[:upper:]')
    
    # Loop through the Roman numeral from right to left
    for (( i=${#roman}-1; i>=0; i-- )); do
        # Get current character
        local char="${roman:$i:1}"
        
        # Map Roman numeral to value
        case "$char" in
            I) value=1 ;;
            V) value=5 ;;
            X) value=10 ;;
            L) value=50 ;;
            C) value=100 ;;
            D) value=500 ;;
            M) value=1000 ;;
            *) value=0 ;;
        esac
        
        # Add or subtract based on Roman numeral rules
        if [ "$value" -ge "$prev" ]; then
            result=$((result + value))
        else
            result=$((result - value))
        fi
        
        prev=$value
    done
    
    echo "$result"
}

# Initialize counters
total_files=0
modified_files=0

# Find all week-*.md files
find . -type f -name "week-*.md" | while read -r file; do
    ((total_files++))
    # echo "Processing: $file"
    
    # Extract the first 3 lines where we expect the title to be
    head_content=$(head -n 3 "$file")
    
    # Check if any of these lines contain a Roman numeral title
    if echo "$head_content" | grep -q "LESSON [IVXLCDM]\+"; then
        # Create a temporary file
        temp_file=$(mktemp)
        
        # Process the file and make the replacement
        while IFS= read -r line; do
            if [[ "$line" =~ LESSON[[:space:]]+([IVXLCDM]+) ]]; then
                roman_numeral="${BASH_REMATCH[1]}"
                arabic_numeral=$(roman_to_arabic "$roman_numeral")
                
                echo "  Found: $line"
                echo "  Converting '$roman_numeral' to '$arabic_numeral'"
                
                # Replace using sed
                new_line=$(echo "$line" | sed "s/LESSON[[:space:]]\+$roman_numeral/LESSON $arabic_numeral/")
                echo "$new_line" >> "$temp_file"
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$file"
        
        # Replace the original file with the modified one
        mv "$temp_file" "$file"
        ((modified_files++))
        echo "  File modified successfully"
    # else
    #     echo "  No Roman numerals found in title"
    fi
done

echo "Summary: Processed $total_files files, modified $modified_files files."