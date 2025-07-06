# Makefile for downloading and organizing Sabbath School lessons

.PHONY: help download-lessons download-test download-dry-run download-pdfs download-pdfs-test convert-pdfs install-deps install-pdf-deps clean list-undone list-progress update-lesson-status first-not-done cleanup-lessons

# Default target
help:
	@echo "Available targets:"
	@echo ""
	@echo "Text Files Workflow:"
	@echo "  download-lessons          - Download all lessons as .txt files"
	@echo "  download-test             - Test download with first 10 .txt files"
	@echo "  download-dry-run          - Preview .txt download without downloading"
	@echo ""
	@echo "PDF Workflow (Better OCR Control):"
	@echo "  download-pdfs             - Download all lessons as .pdf files"
	@echo "  download-pdfs-test        - Test download with first 10 .pdf files" 
	@echo "  convert-pdfs              - Convert PDFs to page-by-page text files"
	@echo "  convert-pdf               - Convert specific PDF file (Usage: make convert-pdf PDF=path/to/file.pdf)"
	@echo "  install-pdf-deps          - Install PDF processing dependencies"
	@echo ""
	@echo "Progress and Status:"
	@echo "  list-progress             - Show completion progress for all languages"
	@echo "  list-undone               - List lessons not completed by language"
	@echo "  first-not-done-en/sw      - Show first undone lesson with source files"
	@echo "  list-undone-with-source   - List undone lessons that have source files"
	@echo "  update-lesson-status      - Update lesson completion status"
	@echo ""
	@echo "Processing:"
	@echo "  cleanup-lessons           - Process OCR lesson files into structured markdown"
	@echo ""
	@echo "Utilities:"
	@echo "  install-deps              - Install required Python dependencies"
	@echo "  clean                     - Remove downloaded files"
	@echo "  help                      - Show this help message"

# Install required dependencies
install-deps:
	pip install requests beautifulsoup4

# Install PDF processing dependencies
install-pdf-deps:
	@echo "Installing PDF processing dependencies..."
	@echo "Note: You may need sudo privileges for system packages"
	sudo apt-get update
	sudo apt-get install -y poppler-utils tesseract-ocr
	pip install requests beautifulsoup4
	@echo "Testing dependencies..."
	python scripts/pdf-to-text.py --check-deps

# Download all lessons
download-lessons:
	@echo "Starting full download of lessons..."
	python scripts/download_lessons.py

# Test download with first 10 files
download-test:
	@echo "Testing download with first 10 files..."
	python scripts/download_lessons.py --test

# Dry run to preview what would be downloaded
download-dry-run:
	@echo "Dry run - previewing download..."
	python scripts/download_lessons.py --dry-run

# Download all lessons as PDF files
download-pdfs:
	@echo "Starting full download of PDF lessons..."
	python scripts/download-pdfs.py

# Test download with first 10 PDF files
download-pdfs-test:
	@echo "Testing PDF download with first 10 files..."
	python scripts/download-pdfs.py --test

# Dry run to preview PDF download
download-pdfs-dry-run:
	@echo "Dry run - previewing PDF download..."
	python scripts/download-pdfs.py --dry-run

# Convert PDFs to page-by-page text files
convert-pdfs:
	@echo "Converting PDFs to page-by-page text files..."
	python scripts/pdf-to-text.py data/pdfs/

# Convert specific PDF file
convert-pdf:
	@if [ -z "$(PDF)" ]; then \
		echo "Usage: make convert-pdf PDF=path/to/file.pdf"; \
		exit 1; \
	fi
	python scripts/pdf-to-text.py "$(PDF)"

# Clean downloaded files
clean:
	@echo "Removing downloaded files..."
	rm -rf data/downloads data/pdfs
	@echo "Cleaned up downloaded files."

# Clean only TXT downloads
clean-txt:
	@echo "Removing TXT downloads..."
	rm -rf data/downloads
	@echo "Cleaned up TXT files."

# Clean only PDF downloads
clean-pdfs:
	@echo "Removing PDF downloads..."
	rm -rf data/pdfs
	@echo "Cleaned up PDF files."

# Check if lessons.json exists
check-lessons-json:
	@if [ ! -f data/lessons.json ]; then \
		echo "Error: data/lessons.json not found!"; \
		exit 1; \
	fi

# Download with dependency check
download-lessons-safe: check-lessons-json install-deps download-lessons

# Test download with dependency check
download-test-safe: check-lessons-json install-deps download-test

# List undone lessons by language
list-undone:
	@echo "Listing undone lessons..."
	python scripts/list-undone-lessons.py

# Show completion progress for all languages
list-progress:
	@echo "Showing completion progress..."
	python scripts/list-undone-lessons.py --progress

# Update lesson completion status (interactive)
update-lesson-status:
	@echo "Update lesson completion status:"
	@echo "Usage examples:"
	@echo "  python scripts/update-lessons-json.py add 1888 Q1 en"
	@echo "  python scripts/update-lessons-json.py status 1888 Q1"
	@echo "  python scripts/update-lessons-json.py languages"

# List undone lessons for specific language
list-undone-en:
	python scripts/list-undone-lessons.py --language en --details

list-undone-sw:
	python scripts/list-undone-lessons.py --language sw --details

# List completed lessons for specific language
list-completed-en:
	python scripts/list-undone-lessons.py --language en --completed --details

list-completed-sw:
	python scripts/list-undone-lessons.py --language sw --completed --details

# Show first undone lesson for language
first-not-done:
	@echo "Usage: make first-not-done-en or first-not-done-sw"

first-not-done-en:
	@echo "First undone English lesson (with source files):"
	python scripts/list-undone-lessons.py --language en --first-undone

first-not-done-sw:
	@echo "First undone Kiswahili lesson (with source files):"
	python scripts/list-undone-lessons.py --language sw --first-undone

# Show languages available
show-languages:
	@echo "Available languages:"
	python scripts/update-lessons-json.py languages

# List undone lessons with source files available
list-undone-with-source:
	@echo "Undone lessons with source files available:"
	python scripts/list-undone-lessons.py --with-source --details

list-undone-en-with-source:
	@echo "Undone English lessons with source files:"
	python scripts/list-undone-lessons.py --language en --with-source --details

list-undone-sw-with-source:
	@echo "Undone Kiswahili lessons with source files:"
	python scripts/list-undone-lessons.py --language sw --with-source --details

# Process OCR lesson files into structured markdown
cleanup-lessons:
	@echo "Usage: make cleanup-lessons YEAR=<year> QUARTER=<quarter> [LANGUAGE=<lang>]"
	@echo "Example: make cleanup-lessons YEAR=1914 QUARTER=Q1 LANGUAGE=en"
	@if [ -z "$(YEAR)" ] || [ -z "$(QUARTER)" ]; then \
		echo "Error: YEAR and QUARTER are required"; \
		exit 1; \
	fi
	python scripts/cleanup-lessons.py $(YEAR) $(QUARTER) $(or $(LANGUAGE),en)