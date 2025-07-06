#!/usr/bin/env python3
"""
Convert PDF files to text page by page using various OCR methods.
Creates individual text files for each page for better processing control.
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess
import json

def check_dependencies():
    """Check if required OCR tools are available"""
    tools = {
        'pdftotext': 'poppler-utils',
        'tesseract': 'tesseract-ocr',
        'pdfimages': 'poppler-utils'
    }
    
    missing = []
    for tool, package in tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(f"{tool} (install {package})")
    
    if missing:
        print("Missing required tools:")
        for tool in missing:
            print(f"  - {tool}")
        print("\nInstall with:")
        print("  sudo apt-get install poppler-utils tesseract-ocr")
        sys.exit(1)

def convert_pdf_with_pdftotext(pdf_path, output_dir):
    """Convert PDF to text using pdftotext (fast, works for text PDFs)"""
    print(f"  Trying pdftotext extraction...")
    
    try:
        # Get total page count
        result = subprocess.run([
            'pdfinfo', str(pdf_path)
        ], capture_output=True, text=True, check=True)
        
        pages = 0
        for line in result.stdout.split('\n'):
            if line.startswith('Pages:'):
                pages = int(line.split(':')[1].strip())
                break
        
        if pages == 0:
            return False, "Could not determine page count"
        
        # Extract each page
        success_count = 0
        for page_num in range(1, pages + 1):
            page_file = output_dir / f"page_{page_num:03d}.txt"
            
            # Skip if already exists
            if page_file.exists():
                success_count += 1
                continue
            
            try:
                result = subprocess.run([
                    'pdftotext', 
                    '-f', str(page_num),
                    '-l', str(page_num),
                    str(pdf_path),
                    str(page_file)
                ], capture_output=True, text=True, check=True)
                
                # Check if we got meaningful text
                if page_file.exists() and page_file.stat().st_size > 10:
                    success_count += 1
                else:
                    page_file.unlink(missing_ok=True)
                    
            except subprocess.CalledProcessError as e:
                print(f"    Error extracting page {page_num}: {e}")
        
        success_rate = success_count / pages
        return success_rate > 0.5, f"Extracted {success_count}/{pages} pages"
        
    except subprocess.CalledProcessError as e:
        return False, f"pdftotext failed: {e}"

def convert_pdf_with_tesseract(pdf_path, output_dir):
    """Convert PDF to text using Tesseract OCR (slower, works for image PDFs)"""
    print(f"  Trying Tesseract OCR extraction...")
    
    try:
        # First convert PDF pages to images
        temp_dir = output_dir / "temp_images"
        temp_dir.mkdir(exist_ok=True)
        
        # Convert PDF to images
        subprocess.run([
            'pdftoppm', 
            '-png',
            str(pdf_path),
            str(temp_dir / "page")
        ], capture_output=True, check=True)
        
        # Get list of image files
        image_files = sorted(temp_dir.glob("page-*.png"))
        
        if not image_files:
            return False, "No images generated from PDF"
        
        success_count = 0
        for i, image_file in enumerate(image_files, 1):
            page_file = output_dir / f"page_{i:03d}.txt"
            
            # Skip if already exists
            if page_file.exists():
                success_count += 1
                continue
            
            try:
                # Run Tesseract OCR
                result = subprocess.run([
                    'tesseract',
                    str(image_file),
                    str(page_file.with_suffix('')),  # tesseract adds .txt automatically
                    '-l', 'eng'
                ], capture_output=True, text=True, check=True)
                
                if page_file.exists() and page_file.stat().st_size > 10:
                    success_count += 1
                
            except subprocess.CalledProcessError as e:
                print(f"    Error OCR'ing page {i}: {e}")
        
        # Cleanup temp images
        for image_file in image_files:
            image_file.unlink(missing_ok=True)
        temp_dir.rmdir()
        
        success_rate = success_count / len(image_files)
        return success_rate > 0.5, f"OCR'd {success_count}/{len(image_files)} pages"
        
    except subprocess.CalledProcessError as e:
        return False, f"Tesseract OCR failed: {e}"

def convert_single_pdf(pdf_path, force_ocr=False):
    """Convert a single PDF file to page-by-page text files"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    # Create output directory
    output_dir = pdf_path.parent / f"{pdf_path.stem}_pages"
    output_dir.mkdir(exist_ok=True)
    
    print(f"Converting: {pdf_path}")
    print(f"Output dir: {output_dir}")
    
    # Try pdftotext first (unless forced OCR)
    if not force_ocr:
        success, message = convert_pdf_with_pdftotext(pdf_path, output_dir)
        print(f"  pdftotext: {message}")
        
        if success:
            # Create metadata file
            create_conversion_metadata(pdf_path, output_dir, "pdftotext")
            return True
    
    # Fall back to Tesseract OCR
    success, message = convert_pdf_with_tesseract(pdf_path, output_dir)
    print(f"  Tesseract OCR: {message}")
    
    if success:
        # Create metadata file
        create_conversion_metadata(pdf_path, output_dir, "tesseract")
        return True
    
    print(f"  ✗ Failed to convert {pdf_path}")
    return False

def create_conversion_metadata(pdf_path, output_dir, method):
    """Create metadata file with conversion information"""
    metadata = {
        'source_pdf': str(pdf_path),
        'conversion_method': method,
        'output_directory': str(output_dir),
        'page_files': sorted([f.name for f in output_dir.glob("page_*.txt")])
    }
    
    metadata_file = output_dir / "conversion_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def convert_lessons_in_directory(directory, force_ocr=False):
    """Convert all PDF lessons in a directory structure"""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory not found: {directory}")
        return
    
    # Find all PDF files
    pdf_files = list(directory.rglob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return
    
    print(f"Found {len(pdf_files)} PDF files to convert")
    
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        if convert_single_pdf(pdf_file, force_ocr):
            successful += 1
        else:
            failed += 1
    
    print(f"\nConversion Summary:")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total: {len(pdf_files)}")

def main():
    parser = argparse.ArgumentParser(description='Convert PDF lessons to page-by-page text files')
    parser.add_argument('input', nargs='?', help='PDF file or directory containing PDFs')
    parser.add_argument('--force-ocr', action='store_true', 
                       help='Force OCR even for text-based PDFs')
    parser.add_argument('--check-deps', action='store_true',
                       help='Check if required dependencies are installed')
    
    args = parser.parse_args()
    
    if args.check_deps:
        check_dependencies()
        print("All required dependencies are installed!")
        return
    
    if not args.input:
        parser.error("input argument is required when not checking dependencies")
    
    # Check dependencies
    check_dependencies()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        convert_single_pdf(input_path, args.force_ocr)
    elif input_path.is_dir():
        convert_lessons_in_directory(input_path, args.force_ocr)
    else:
        print(f"Error: Invalid input path: {input_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()