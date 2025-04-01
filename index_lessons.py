#!/usr/bin/env python3
import os
import yaml
import json
import re
from pathlib import Path

def parse_lessons_directory(base_dir="lessons"):
    """
    Traverses the lessons directory structure and generates a structured JSON representation.
    
    Directory structure: lessons/org/{decade}/{year}/{quarter}/{lang}
    """
    result = {
        "organizations": {}
    }
    
    # Check if base directory exists
    if not os.path.isdir(base_dir):
        print(f"Error: Base directory '{base_dir}' not found.")
        return result
    
    # Iterate through organizations
    for org in os.listdir(base_dir):
        org_path = os.path.join(base_dir, org)
        if not os.path.isdir(org_path):
            continue
        
        result["organizations"][org] = {
            "name": org,
            "years": {}
        }
        
        # Iterate through decades
        for decade in os.listdir(org_path):
            decade_path = os.path.join(org_path, decade)
            if not os.path.isdir(decade_path):
                continue
            
            # Iterate through years
            for year in os.listdir(decade_path):
                year_path = os.path.join(decade_path, year)
                if not os.path.isdir(year_path):
                    continue
                
                if year not in result["organizations"][org]["years"]:
                    result["organizations"][org]["years"][year] = {
                        "quarters": {}
                    }
                
                # Iterate through quarters
                for quarter in os.listdir(year_path):
                    quarter_path = os.path.join(year_path, quarter)
                    if not os.path.isdir(quarter_path):
                        continue
                    
                    # Extract quarter number (q1, q2, q3, q4)
                    quarter_match = re.match(r'q(\d+)', quarter)
                    if not quarter_match:
                        continue
                    
                    quarter_num = quarter_match.group(1)
                    
                    result["organizations"][org]["years"][year]["quarters"][quarter] = {
                        "languages": {}
                    }
                    
                    # Iterate through languages
                    for lang in os.listdir(quarter_path):
                        lang_path = os.path.join(quarter_path, lang)
                        if not os.path.isdir(lang_path):
                            continue
                        
                        # Construct expected PDF path
                        pdf_filename = f"sabbath_school_lesson_{year}_{quarter}_{lang}.pdf"
                        pdf_path = os.path.join(lang_path, "output", pdf_filename)
                        
                        # Check if PDF exists
                        if not os.path.isfile(pdf_path):
                            print(f"Warning: PDF not found at {pdf_path}")
                            continue
                        
                        # Look for config.yaml to get thumbnail
                        config_path = os.path.join(lang_path, "config.yaml")
                        thumbnail_path = None
                        
                        if os.path.isfile(config_path):
                            try:
                                with open(config_path, 'r') as f:
                                    config = yaml.safe_load(f)
                                    # Look for front cover thumbnail in config
                                    if config and 'front_cover_svg' in config:
                                        thumbnail_path = config['front_cover_svg']
                                    else:
                                        # Try to find cover SVG files in standard locations
                                        possible_covers = [
                                            os.path.join(lang_path, "covers", "front.svg"),
                                            os.path.join(lang_path, "covers", "front.use.png"),
                                            os.path.join(lang_path, "assets", "front_cover.svg")
                                        ]
                                        for cover in possible_covers:
                                            if os.path.isfile(cover):
                                                thumbnail_path = cover
                                                break
                            except Exception as e:
                                print(f"Error reading config file {config_path}: {e}")
                        
                        # Store language data
                        lesson_info = {
                            "pdf_path": pdf_path,
                            "thumbnail_path": thumbnail_path
                        }
                        
                        # Make paths relative for web usage
                        lesson_info["pdf_path"] = os.path.relpath(pdf_path, base_dir)
                        if thumbnail_path:
                            if os.path.isabs(thumbnail_path):
                                lesson_info["thumbnail_path"] = thumbnail_path
                            else:
                                lesson_info["thumbnail_path"] = os.path.relpath(Path(lang_path) / thumbnail_path, base_dir)
                        
                        result["organizations"][org]["years"][year]["quarters"][quarter]["languages"][lang] = lesson_info
    
    # Add metadata for filtering
    result["metadata"] = {
        "available_organizations": sorted(list(result["organizations"].keys())),
        "available_years": sorted(list(set(year for org in result["organizations"].values() for year in org["years"].keys()))),
        "available_quarters": ["q1", "q2", "q3", "q4"],
        "available_languages": sorted(list(set(
            lang 
            for org in result["organizations"].values() 
            for year in org["years"].values() 
            for quarter in year["quarters"].values()
            for lang in quarter["languages"].keys()
        )))
    }
    
    return result

def main():
    # Parse the lessons directory
    lessons_data = parse_lessons_directory()
    
    # Write the JSON output
    output_file = "lessons_index.json"
    with open(output_file, 'w') as f:
        json.dump(lessons_data, f, indent=2)
    
    print(f"Lesson index created successfully at {output_file}")
    
    # Print summary statistics
    orgs = lessons_data["metadata"]["available_organizations"]
    years = lessons_data["metadata"]["available_years"]
    languages = lessons_data["metadata"]["available_languages"]
    
    print(f"\nSummary:")
    print(f"- Organizations: {', '.join(orgs)}")
    print(f"- Years: {', '.join(years)}")
    print(f"- Languages: {', '.join(languages)}")
    
    # Count total lessons
    total_lessons = 0
    for org in lessons_data["organizations"].values():
        for year in org["years"].values():
            for quarter in year["quarters"].values():
                total_lessons += len(quarter["languages"])
    
    print(f"- Total lessons indexed: {total_lessons}")

if __name__ == "__main__":
    main()