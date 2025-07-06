#!/usr/bin/env python3
"""
Download PDF lessons from https://sslpdfs.gospelsounders.org/
and organize them into decade/year/quarter structure.
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from pathlib import Path
import time
import shutil

BASE_URL = "https://sslpdfs.gospelsounders.org/"
LESSONS_JSON = "data/lessons.json"

def load_lessons_metadata():
    """Load lessons metadata from lessons.json"""
    with open(LESSONS_JSON, 'r') as f:
        data = json.load(f)
    return data['lessons']

def scrape_pdf_links():
    """Scrape all .pdf links from the SSL PDFs site"""
    print("Scraping .pdf links from SSL PDFs site...")
    
    try:
        response = requests.get(BASE_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching main page: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = []
    
    # Find all links ending with .pdf
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf'):
            full_url = urljoin(BASE_URL, href)
            pdf_links.append(full_url)
    
    print(f"Found {len(pdf_links)} .pdf links")
    return pdf_links

def parse_pdf_filename(url):
    """Parse PDF filename to extract year, quarter, and lesson number"""
    filename = os.path.basename(url)
    
    # Pattern: SS[YYYYMMDD-NN].pdf where YYYY=year, MM=month, DD=day, NN=lesson
    match = re.match(r'SS(\d{4})(\d{2})(\d{2})-(\d{2})\.pdf', filename)
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

def get_decade(year):
    """Get decade string from year (e.g., 1880s, 1890s, etc.)"""
    decade = (year // 10) * 10
    return f"{decade}s"

def handle_biannual_quarter(quarter_str):
    """Handle biannual quarters like Q1-Q2 -> Q1"""
    if '-' in quarter_str:
        return quarter_str.split('-')[0]
    return quarter_str

def create_pdf_directory_structure(year, quarter):
    """Create directory structure: decade/year/quarter for PDFs"""
    decade = get_decade(year)
    quarter = handle_biannual_quarter(quarter)
    quarter_str = quarter.lower()
    
    path = Path(f"data/pdfs/{decade}/{year}/{quarter_str}")
    path.mkdir(parents=True, exist_ok=True)
    return path

def download_pdf(url, output_path):
    """Download a single PDF file"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

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

def download_lesson_pdf(url, parsed_info, lesson_meta=None, dry_run=False):
    """Download a single lesson PDF"""
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
    lesson_dir = create_pdf_directory_structure(year, quarter)
    
    if dry_run:
        print(f"  Would create: {lesson_dir}")
        return True
    
    # Create output filename
    output_filename = f"lesson_{lesson_num:02d}.pdf"
    output_path = lesson_dir / output_filename
    
    # Skip if file already exists
    if output_path.exists():
        print(f"  ⚠️  Already exists: {output_path}")
        return False
    
    print(f"  Downloading: {url}")
    
    if download_pdf(url, output_path):
        print(f"  ✓ Downloaded: {output_path}")
        return True
    else:
        print(f"  ✗ Failed: {url}")
        return False

def main():
    """Main function to download and organize PDF lessons"""
    import sys
    
    # Check if lessons.json exists
    lessons_file = Path(LESSONS_JSON)
    if not lessons_file.exists():
        print(f"Error: {LESSONS_JSON} not found!")
        sys.exit(1)
    
    # Load lessons data
    lessons_metadata = load_lessons_metadata()
    
    # Check command line arguments
    dry_run = '--dry-run' in sys.argv
    test_mode = '--test' in sys.argv
    
    if dry_run:
        print("DRY RUN MODE - No files will be downloaded")
    
    if test_mode:
        print("TEST MODE - Only processing first 10 links")
    
    # Scrape .pdf links from the site
    pdf_links = scrape_pdf_links()
    
    if not pdf_links:
        print("No .pdf links found. Exiting.")
        return
    
    if test_mode:
        pdf_links = pdf_links[:10]
    
    # Download PDFs
    successful = 0
    failed = 0
    skipped = 0
    
    for i, url in enumerate(pdf_links, 1):
        print(f"\n[{i}/{len(pdf_links)}] ", end="")
        
        parsed_info = parse_pdf_filename(url)
        if not parsed_info:
            print(f"Could not parse filename: {url}")
            failed += 1
            continue
        
        # Try to match with metadata
        lesson_meta = match_lesson_with_metadata(parsed_info, lessons_metadata)
        
        result = download_lesson_pdf(url, parsed_info, lesson_meta, dry_run)
        
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
    print(f"  Total: {len(pdf_links)}")

if __name__ == "__main__":
    main()