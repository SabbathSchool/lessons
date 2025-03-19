import os
import re
import json
import sys
import shutil
from pathlib import Path

def extract_first_lines(file_path, num_lines=4):
    """Extract the first non-blank lines from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = []
        for line in f:
            line = line.strip()
            if line:  # If line is not empty
                lines.append(line)
                if len(lines) >= num_lines:
                    break
        return lines

def extract_titles():
    """Extract titles from week files and save to individual files in for-titling directory."""
    # Create output directory if it doesn't exist, or clear it if it does
    output_dir = Path("for-titling")
    if output_dir.exists():
        # Remove all files in the directory except combined.md
        for file_path in output_dir.glob("*.md"):
            if file_path.name != "combined.md":
                file_path.unlink()
    else:
        output_dir.mkdir()
    
    # Walk through the directory structure
    root_dir = Path(".")
    
    decade_pattern = re.compile(r'\d{4}s$')
    
    for decade_dir in root_dir.iterdir():
        if not decade_dir.is_dir() or not decade_pattern.match(decade_dir.name):
            continue
            
        for year_dir in decade_dir.iterdir():
            if not year_dir.is_dir():
                continue
                
            for quarter_dir in year_dir.iterdir():
                if not quarter_dir.is_dir() or not quarter_dir.name.startswith('q'):
                    continue
                    
                for lang_dir in quarter_dir.iterdir():
                    if not lang_dir.is_dir():
                        continue
                    
                    # Check if contents.json exists in this directory
                    contents_json = lang_dir / "contents.json"
                    if contents_json.exists():
                        continue
                    
                    # This directory doesn't have contents.json, process the week files
                    output_lines = []
                    
                    # Sort week files naturally
                    week_files = sorted(
                        [f for f in lang_dir.glob("week-*.md")],
                        key=lambda x: int(re.search(r'week-(\d+)\.md', x.name).group(1))
                    )
                    
                    for week_file in week_files:
                        first_lines = extract_first_lines(week_file)
                        output_lines.append(f"## {week_file.stem}")
                        output_lines.extend(first_lines)
                        output_lines.append("")  # Add a blank line between weeks
                    
                    if output_lines:
                        # Create output file name
                        output_filename = f"{decade_dir.name}-{year_dir.name}-{quarter_dir.name}-{lang_dir.name}.md"
                        output_path = output_dir / output_filename
                        
                        # Write the output
                        with open(output_path, 'w', encoding='utf-8') as out_file:
                            out_file.write("\n".join(output_lines))
                        
                        print(f"Created {output_path}")

def combine_titles():
    """Combine all title files in for-titling directory into a single combined.md file."""
    output_dir = Path("for-titling")
    if not output_dir.exists():
        print("for-titling directory does not exist.")
        return
    
    combined_file = output_dir / "combined.md"
    
    with open(combined_file, 'w', encoding='utf-8') as combined:
        # Get all md files except combined.md
        title_files = [f for f in output_dir.glob("*.md") if f.name != "combined.md"]
        
        for file_path in sorted(title_files):
            # Extract decade, year, quarter, language from filename
            match = re.match(r'(\d{4}s)-(\d{4})-(q\d)-([\w]+)\.md', file_path.name)
            if match:
                decade, year, quarter, language = match.groups()
                
                # Create path for title.json that would be created
                original_path = f"{decade}/{year}/{quarter}/{language}/contents.json"
                
                # Write commented file path
                combined.write(f"<!-- This is a single file -->\n")
                combined.write(f"<!-- Save to: {original_path} -->\n\n")
                
                # Append file contents
                with open(file_path, 'r', encoding='utf-8') as input_file:
                    combined.write(input_file.read())
                    
                # Add separator between files
                combined.write("\n\n---\n\n")
        
        print(f"Created {combined_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py [extract|combine]")
        return
    
    command = sys.argv[1].lower()
    
    if command == "extract":
        extract_titles()
    elif command == "combine":
        combine_titles()
    else:
        print("Invalid command. Use 'extract' or 'combine'.")

if __name__ == "__main__":
    main()