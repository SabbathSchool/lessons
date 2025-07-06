#!/usr/bin/env python3
"""
Download script for Sabbath School lessons from https://sslpdfs.gospelsounders.org/
Organizes lessons by decade/year/quarter structure
"""

import json
import requests
import os
from pathlib import Path
import time
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re

def create_directory_structure(year, quarter):
    """Create the proper directory structure for a lesson"""
    decade = f"{(year // 10) * 10}s"
    # Handle biannual quarters like Q1-Q2 -> Q1
    if '-' in quarter:
        quarter = quarter.split('-')[0]
    quarter_str = quarter.lower()
    
    path = Path(f"data/downloads/{decade}/{year}/{quarter_str}")
    path.mkdir(parents=True, exist_ok=True)
    return path

def scrape_txt_links():
    """Scrape all .txt links from the SSL PDFs site"""
    print("Scraping .txt links from SSL PDFs site...")
    base_url = "https://sslpdfs.gospelsounders.org/"
    
    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    txt_links = []
    
    # Find all links ending with .txt
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.txt'):
            full_url = urljoin(base_url, href)
            txt_links.append(full_url)
    
    print(f"Found {len(txt_links)} .txt links")
    return txt_links

def parse_filename(url):
    """Parse filename to extract year, quarter, and lesson number"""
    filename = os.path.basename(url)
    
    # Pattern: SS[YYYYMMDD-NN].txt where YYYY=year, MM=month, DD=day, NN=lesson
    match = re.match(r'SS(\d{4})(\d{2})(\d{2})-(\d{2})\.txt', filename)
    if not match:
        return None
    
    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(3))
    lesson_num = int(match.group(4))
    
    # Convert month to quarter
    if month in [1, 2, 3]:
        quarter = "Q1"
    elif month in [4, 5, 6]:
        quarter = "Q2"
    elif month in [7, 8, 9]:
        quarter = "Q3"
    elif month in [10, 11, 12]:
        quarter = "Q4"
    else:
        quarter = "Q1"  # default
    
    return {
        'year': year,
        'quarter': quarter,
        'lesson_num': lesson_num,
        'filename': filename
    }

def match_lesson_with_metadata(parsed_info, lessons_metadata):
    """Match parsed lesson info with metadata from lessons.json"""
    for lesson in lessons_metadata:
        if lesson['year'] == parsed_info['year']:
            # Handle biannual quarters
            if '-' in lesson['quarter']:
                quarters = lesson['quarter'].split('-')
                if parsed_info['quarter'] in quarters:
                    return lesson
            elif lesson['quarter'] == parsed_info['quarter']:
                return lesson
    return None

def download_file(url, filepath, max_retries=3):
    """Download a file with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return True
            elif response.status_code == 404:
                return False  # File not found
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    return False

def download_lesson(url, parsed_info, lesson_meta=None, dry_run=False):
    """Download a single lesson"""
    year = parsed_info['year']
    quarter = parsed_info['quarter']
    lesson_num = parsed_info['lesson_num']
    
    # Use metadata quarter if available, otherwise use parsed quarter
    if lesson_meta:
        quarter = lesson_meta['quarter']
        title = lesson_meta['title']
    else:
        title = f"Lesson {lesson_num}"
    
    print(f"Processing: {year} {quarter} - {title}")
    
    # Create directory structure
    lesson_dir = create_directory_structure(year, quarter)
    
    if dry_run:
        print(f"  Would create: {lesson_dir}")
        return True
    
    # Create output filename
    output_filename = f"lesson_{lesson_num:02d}.txt"
    output_path = lesson_dir / output_filename
    
    # Skip if file already exists
    if output_path.exists():
        print(f"  ⚠️  Already exists: {output_path}")
        return False
    
    print(f"  Downloading: {url}")
    
    if download_file(url, output_path):
        print(f"  ✓ Downloaded: {output_path}")
        return True
    else:
        print(f"  ✗ Failed: {url}")
        return False

def main():
    """Main function to download all lessons"""
    # Check if lessons.json exists
    lessons_file = Path("data/lessons.json")
    if not lessons_file.exists():
        print("Error: data/lessons.json not found!")
        sys.exit(1)
    
    # Load lessons data
    with open(lessons_file, 'r') as f:
        data = json.load(f)
    
    lessons_metadata = data['lessons']
    
    # Check command line arguments
    dry_run = '--dry-run' in sys.argv
    test_mode = '--test' in sys.argv
    
    if dry_run:
        print("DRY RUN MODE - No files will be downloaded")
    
    if test_mode:
        print("TEST MODE - Only processing first 10 links")
    
    # Scrape .txt links from the site
    txt_links = scrape_txt_links()
    
    if not txt_links:
        print("No .txt links found. Exiting.")
        return
    
    if test_mode:
        txt_links = txt_links[:10]
    
    # Download lessons
    successful = 0
    failed = 0
    skipped = 0
    
    for i, url in enumerate(txt_links, 1):
        print(f"\n[{i}/{len(txt_links)}] ", end="")
        
        parsed_info = parse_filename(url)
        if not parsed_info:
            print(f"Could not parse filename: {url}")
            failed += 1
            continue
        
        # Try to match with metadata
        lesson_meta = match_lesson_with_metadata(parsed_info, lessons_metadata)
        
        result = download_lesson(url, parsed_info, lesson_meta, dry_run)
        
        if result is True:
            successful += 1
        elif result is False and not dry_run:
            skipped += 1
        else:
            failed += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    # Summary
    print(f"\n\nSummary:")
    print(f"  Successful: {successful}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(txt_links)}")

if __name__ == "__main__":
    main()