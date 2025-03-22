#!/bin/bash

# Check if a directory was supplied
if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIRECTORY="$1"

# Check if the directory exists
if [ ! -d "$DIRECTORY" ]; then
    echo "Error: Directory '$DIRECTORY' does not exist."
    exit 1
fi

# Change to the specified directory
cd "$DIRECTORY" || exit 1

# Initialize a counter for file numbering
count=1

# Create a temporary file to store filenames
temp_file=$(mktemp)

# Get all regular files in chronological order, skipping the total line
ls -ltr | awk 'NR>1 && !/^d/ {print $0}' > "$temp_file"

# Process each line from the temp file
while IFS= read -r line; do
    # Extract the filename, which might contain spaces
    # This handles filenames with spaces by looking at everything after the date/time field
    # The date/time field is the 8th field in ls -ltr output
    filename=$(echo "$line" | awk '{for(i=9;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ $//')
    
    # Skip if it's not a regular file or if filename is empty
    if [ ! -f "$filename" ] || [ -z "$filename" ]; then
        continue
    fi
    
    # Format the counter with leading zero if needed
    formatted_count=$(printf "%02d" $count)
    
    # Create the new filename
    new_filename="week-${formatted_count}.md"
    
    # Rename the file
    echo "Renaming '$filename' to '$new_filename'"
    mv -i "$filename" "$new_filename"
    
    # Increment the counter
    ((count++))
done < "$temp_file"

# Clean up
rm "$temp_file"

echo "Renaming complete. Renamed $((count-1)) files."