#!/usr/bin/env python3
"""
Script to list lessons that have not been completed by language
"""

import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict
import os

LESSONS_JSON_PATH = "data/lessons.json"
LESSONS_DATA_PATH = "data/lessons"
DOWNLOADS_PATH = "data/downloads"

def load_lessons():
    """Load lessons from JSON file"""
    try:
        with open(LESSONS_JSON_PATH, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: {LESSONS_JSON_PATH} not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {LESSONS_JSON_PATH}")
        sys.exit(1)

def check_lesson_completed_on_filesystem(lesson, language):
    """Check if a lesson is completed by looking at the file system"""
    year = lesson['year']
    quarter = lesson['quarter'].lower()
    decade = f"{(year // 10) * 10}s"
    
    # Handle biannual quarters like Q1-Q2 -> q1
    if '-' in quarter:
        quarter = quarter.split('-')[0].lower()
    
    lesson_dir = Path(LESSONS_DATA_PATH) / decade / str(year) / quarter / language
    
    if not lesson_dir.exists():
        return False
    
    # Check for key files that indicate completion
    required_files = ['front-matter.md', 'week-01.md']
    optional_files = ['back-matter.md', 'contents.json']
    
    # At minimum, we need front-matter and at least one week
    for required_file in required_files:
        if not (lesson_dir / required_file).exists():
            return False
    
    return True

def check_source_files_exist(lesson):
    """Check if source files exist in data/downloads for this lesson"""
    year = lesson['year']
    quarter = lesson['quarter'].lower()
    decade = f"{(year // 10) * 10}s"
    
    # Handle biannual quarters like Q1-Q2 -> q1
    if '-' in quarter:
        quarter = quarter.split('-')[0].lower()
    
    downloads_dir = Path(DOWNLOADS_PATH) / decade / str(year) / quarter
    
    if not downloads_dir.exists():
        return False
    
    # Check for lesson text files (lesson_01.txt, lesson_02.txt, etc.)
    lesson_files = list(downloads_dir.glob("lesson_*.txt"))
    return len(lesson_files) > 0

def get_all_languages():
    """Get all languages by scanning the file system"""
    languages_from_filesystem = set(['en'])  # Always include English as baseline
    
    # Get languages from file system
    lessons_path = Path(LESSONS_DATA_PATH)
    if lessons_path.exists():
        for decade_dir in lessons_path.iterdir():
            if decade_dir.is_dir() and decade_dir.name.endswith('s'):
                for year_dir in decade_dir.iterdir():
                    if year_dir.is_dir() and year_dir.name.isdigit():
                        for quarter_dir in year_dir.iterdir():
                            if quarter_dir.is_dir() and quarter_dir.name.startswith('q'):
                                for lang_dir in quarter_dir.iterdir():
                                    if lang_dir.is_dir():
                                        languages_from_filesystem.add(lang_dir.name)
    
    return sorted(list(languages_from_filesystem))

def get_undone_lessons(target_language=None):
    """Get lessons that haven't been completed for the specified language"""
    data = load_lessons()
    lessons = data['lessons']
    
    if target_language:
        languages_to_check = [target_language]
    else:
        languages_to_check = get_all_languages()
    
    undone_by_language = defaultdict(list)
    
    for lesson in lessons:
        for lang in languages_to_check:
            # Check if lesson is completed on filesystem
            completed_on_filesystem = check_lesson_completed_on_filesystem(lesson, lang)
            
            # Also check JSON metadata if available
            completed_languages_json = lesson.get('languages_completed', [])
            completed_in_json = lang in completed_languages_json
            
            # A lesson is completed if it exists on filesystem OR is marked in JSON
            if not (completed_on_filesystem or completed_in_json):
                undone_by_language[lang].append(lesson)
    
    return undone_by_language

def get_completed_lessons(target_language=None):
    """Get lessons that have been completed for the specified language"""
    data = load_lessons()
    lessons = data['lessons']
    
    if target_language:
        languages_to_check = [target_language]
    else:
        languages_to_check = get_all_languages()
    
    completed_by_language = defaultdict(list)
    
    for lesson in lessons:
        for lang in languages_to_check:
            # Check if lesson is completed on filesystem
            completed_on_filesystem = check_lesson_completed_on_filesystem(lesson, lang)
            
            # Also check JSON metadata if available
            completed_languages_json = lesson.get('languages_completed', [])
            completed_in_json = lang in completed_languages_json
            
            # A lesson is completed if it exists on filesystem OR is marked in JSON
            if completed_on_filesystem or completed_in_json:
                completed_by_language[lang].append(lesson)
    
    return completed_by_language

def filter_lessons_by_year_range(lessons, start_year=None, end_year=None):
    """Filter lessons by year range"""
    if start_year is None and end_year is None:
        return lessons
    
    filtered = []
    for lesson in lessons:
        year = lesson['year']
        if start_year and year < start_year:
            continue
        if end_year and year > end_year:
            continue
        filtered.append(lesson)
    
    return filtered

def print_lessons_summary(lessons_by_language, title, show_details=False):
    """Print a summary of lessons"""
    print(f"\n{title}")
    print("=" * len(title))
    
    if not lessons_by_language:
        print("No lessons found.")
        return
    
    for language, lessons in lessons_by_language.items():
        count = len(lessons)
        print(f"\n{language.upper()}: {count} lessons")
        
        if show_details and lessons:
            # Group by decade
            decades = defaultdict(list)
            for lesson in lessons:
                decade = f"{(lesson['year'] // 10) * 10}s"
                decades[decade].append(lesson)
            
            for decade in sorted(decades.keys()):
                decade_lessons = decades[decade]
                print(f"  {decade}: {len(decade_lessons)} lessons")
                
                # Group by year
                years = defaultdict(list)
                for lesson in decade_lessons:
                    years[lesson['year']].append(lesson)
                
                for year in sorted(years.keys()):
                    year_lessons = years[year]
                    quarters = [lesson['quarter'] for lesson in year_lessons]
                    print(f"    {year}: {', '.join(sorted(quarters))}")

def print_language_progress():
    """Print progress for all languages"""
    data = load_lessons()
    total_lessons = len(data['lessons'])
    languages = get_all_languages()
    
    print("\nLanguage Completion Progress")
    print("=" * 30)
    print(f"Total lessons: {total_lessons}")
    
    completed_by_language = get_completed_lessons()
    
    for lang in languages:
        completed_count = len(completed_by_language.get(lang, []))
        percentage = (completed_count / total_lessons) * 100 if total_lessons > 0 else 0
        print(f"{lang.upper()}: {completed_count}/{total_lessons} ({percentage:.1f}%)")

def get_first_undone_lesson(language):
    """Get the first undone lesson for a language that has source files available"""
    undone_lessons = get_undone_lessons(language)
    
    if language not in undone_lessons or not undone_lessons[language]:
        return None
    
    # Sort by year and quarter
    lessons = undone_lessons[language]
    lessons.sort(key=lambda x: (x['year'], x['quarter']))
    
    # Find first lesson that has source files available
    for lesson in lessons:
        if check_source_files_exist(lesson):
            return lesson
    
    return None

def main():
    parser = argparse.ArgumentParser(description='List lessons completion status by language')
    parser.add_argument('--language', '-l', help='Target language (en, sw, etc.)')
    parser.add_argument('--start-year', type=int, help='Start year filter')
    parser.add_argument('--end-year', type=int, help='End year filter')
    parser.add_argument('--completed', '-c', action='store_true', 
                       help='Show completed lessons instead of undone')
    parser.add_argument('--details', '-d', action='store_true',
                       help='Show detailed breakdown by decade and year')
    parser.add_argument('--progress', '-p', action='store_true',
                       help='Show overall progress for all languages')
    parser.add_argument('--first-undone', '-f', action='store_true',
                       help='Show first undone lesson for language')
    parser.add_argument('--with-source', '-s', action='store_true',
                       help='Only show lessons that have source files available')
    
    args = parser.parse_args()
    
    if args.progress:
        print_language_progress()
        return
    
    if args.first_undone:
        if not args.language:
            print("Error: --first-undone requires --language argument")
            sys.exit(1)
        
        first_lesson = get_first_undone_lesson(args.language)
        if first_lesson:
            print(f"First undone lesson for {args.language.upper()}: {first_lesson['year']} {first_lesson['quarter']} - {first_lesson['title']}")
        else:
            print(f"No undone lessons with source files found for {args.language.upper()}")
        return
    
    if args.completed:
        lessons_by_language = get_completed_lessons(args.language)
        title = f"Completed Lessons"
    else:
        lessons_by_language = get_undone_lessons(args.language)
        title = f"Undone Lessons"
    
    # Filter to only lessons with source files if requested
    if args.with_source:
        filtered_lessons_by_language = {}
        for lang, lessons in lessons_by_language.items():
            filtered_lessons = [lesson for lesson in lessons if check_source_files_exist(lesson)]
            if filtered_lessons:
                filtered_lessons_by_language[lang] = filtered_lessons
        lessons_by_language = filtered_lessons_by_language
        title += " (with source files)"
    
    if args.language:
        title += f" ({args.language.upper()})"
    
    # Apply year filtering
    if args.start_year or args.end_year:
        filtered_lessons_by_language = {}
        for lang, lessons in lessons_by_language.items():
            filtered = filter_lessons_by_year_range(lessons, args.start_year, args.end_year)
            if filtered:  # Only include languages with lessons in the range
                filtered_lessons_by_language[lang] = filtered
        lessons_by_language = filtered_lessons_by_language
        
        year_filter = []
        if args.start_year:
            year_filter.append(f"from {args.start_year}")
        if args.end_year:
            year_filter.append(f"to {args.end_year}")
        if year_filter:
            title += f" ({' '.join(year_filter)})"
    
    print_lessons_summary(lessons_by_language, title, args.details)
    
    # Show summary counts
    if not args.language:
        total_undone = sum(len(lessons) for lessons in lessons_by_language.values())
        language_count = len(lessons_by_language)
        print(f"\nSummary: {total_undone} lesson-language combinations across {language_count} languages")

if __name__ == "__main__":
    main()