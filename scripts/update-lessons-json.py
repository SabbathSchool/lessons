#!/usr/bin/env python3
"""
Script to update lessons.json with language completion status
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

LESSONS_JSON_PATH = "data/lessons.json"

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

def save_lessons(data):
    """Save lessons to JSON file"""
    try:
        with open(LESSONS_JSON_PATH, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Updated {LESSONS_JSON_PATH}")
    except Exception as e:
        print(f"Error saving {LESSONS_JSON_PATH}: {e}")
        sys.exit(1)

def find_lesson(lessons, year, quarter):
    """Find lesson by year and quarter"""
    for lesson in lessons:
        if lesson['year'] == year and lesson['quarter'] == quarter:
            return lesson
    return None

def add_language_completion(year, quarter, language):
    """Add language completion to a lesson"""
    data = load_lessons()
    lessons = data['lessons']
    
    lesson = find_lesson(lessons, year, quarter)
    if not lesson:
        print(f"Error: Lesson {year} {quarter} not found!")
        return False
    
    # Initialize languages_completed if it doesn't exist
    if 'languages_completed' not in lesson:
        lesson['languages_completed'] = []
    
    # Add language if not already present
    if language not in lesson['languages_completed']:
        lesson['languages_completed'].append(language)
        lesson['last_updated'] = datetime.now().isoformat()
        
        save_lessons(data)
        print(f"Added {language} completion for {year} {quarter}")
        return True
    else:
        print(f"Language {language} already marked as completed for {year} {quarter}")
        return False

def remove_language_completion(year, quarter, language):
    """Remove language completion from a lesson"""
    data = load_lessons()
    lessons = data['lessons']
    
    lesson = find_lesson(lessons, year, quarter)
    if not lesson:
        print(f"Error: Lesson {year} {quarter} not found!")
        return False
    
    if 'languages_completed' in lesson and language in lesson['languages_completed']:
        lesson['languages_completed'].remove(language)
        lesson['last_updated'] = datetime.now().isoformat()
        
        save_lessons(data)
        print(f"Removed {language} completion for {year} {quarter}")
        return True
    else:
        print(f"Language {language} not found in completed languages for {year} {quarter}")
        return False

def list_lesson_status(year, quarter):
    """List completion status for a specific lesson"""
    data = load_lessons()
    lessons = data['lessons']
    
    lesson = find_lesson(lessons, year, quarter)
    if not lesson:
        print(f"Error: Lesson {year} {quarter} not found!")
        return
    
    print(f"\nLesson: {year} {quarter} - {lesson['title']}")
    print(f"Type: {lesson['type']}")
    print(f"Weeks: {lesson.get('weeks', 'N/A')}")
    
    completed_languages = lesson.get('languages_completed', [])
    if completed_languages:
        print(f"Completed languages: {', '.join(completed_languages)}")
    else:
        print("Completed languages: None")
    
    if 'last_updated' in lesson:
        print(f"Last updated: {lesson['last_updated']}")

def get_all_languages():
    """Get all languages that appear in lessons.json"""
    data = load_lessons()
    lessons = data['lessons']
    
    all_languages = set()
    for lesson in lessons:
        completed = lesson.get('languages_completed', [])
        all_languages.update(completed)
    
    return sorted(list(all_languages))

def main():
    parser = argparse.ArgumentParser(description='Update lessons.json with language completion status')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add language completion
    add_parser = subparsers.add_parser('add', help='Add language completion')
    add_parser.add_argument('year', type=int, help='Lesson year')
    add_parser.add_argument('quarter', help='Lesson quarter (Q1, Q2, Q3, Q4, or Q1-Q2)')
    add_parser.add_argument('language', help='Language code (en, sw, etc.)')
    
    # Remove language completion
    remove_parser = subparsers.add_parser('remove', help='Remove language completion')
    remove_parser.add_argument('year', type=int, help='Lesson year')
    remove_parser.add_argument('quarter', help='Lesson quarter (Q1, Q2, Q3, Q4, or Q1-Q2)')
    remove_parser.add_argument('language', help='Language code (en, sw, etc.)')
    
    # List lesson status
    status_parser = subparsers.add_parser('status', help='Show lesson completion status')
    status_parser.add_argument('year', type=int, help='Lesson year')
    status_parser.add_argument('quarter', help='Lesson quarter (Q1, Q2, Q3, Q4, or Q1-Q2)')
    
    # List all languages
    langs_parser = subparsers.add_parser('languages', help='List all languages in lessons.json')
    
    args = parser.parse_args()
    
    if args.command == 'add':
        add_language_completion(args.year, args.quarter, args.language)
    elif args.command == 'remove':
        remove_language_completion(args.year, args.quarter, args.language)
    elif args.command == 'status':
        list_lesson_status(args.year, args.quarter)
    elif args.command == 'languages':
        languages = get_all_languages()
        print("Languages found in lessons.json:")
        for lang in languages:
            print(f"  {lang}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()