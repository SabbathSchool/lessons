# Sabbath School Lessons Project

A monorepo for processing, organizing, and managing Sabbath School lessons with OCR cleanup, translation workflows, and progress tracking.

## Project Structure

```
├── apps/                    # Future applications
├── packages/               # Shared packages
├── scripts/               # Python scripts for processing
│   ├── download-lessons.py     # Download lessons from SSL PDFs
│   ├── update-lessons-json.py  # Update lesson completion status
│   └── list-undone-lessons.py  # Track processing progress
├── data/                  # Data files and processed lessons
│   ├── lessons.json           # Lesson metadata and completion status
│   ├── downloads/             # Downloaded raw text files
│   └── lessons/              # Processed markdown files
│       └── [DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/
├── .claude/commands/      # Claude Code commands
│   └── cleanup-lessons.md     # OCR cleanup and formatting command
├── Makefile              # Build and utility commands
├── package.json          # Monorepo configuration
└── turbo.json           # Turbo build configuration
```

## Quick Start

### 1. Install Dependencies
```bash
make install-deps
```

### 2. Download Lessons

#### Option A: Text Files (Direct Processing)
```bash
# Download all lessons as .txt files
make download-lessons

# Test with first 10 files
make download-test

# Preview without downloading
make download-dry-run
```

#### Option B: PDF Files (Better OCR Control)
```bash
# Install PDF processing dependencies
make install-pdf-deps

# Download all lessons as .pdf files
make download-pdfs

# Test with first 10 PDF files
make download-pdfs-test

# Convert PDFs to page-by-page text files
make convert-pdfs

# Convert specific PDF
make convert-pdf PDF=path/to/lesson.pdf
```

### 3. Check Progress
```bash
# Show completion progress for all languages
make list-progress

# List undone lessons
make list-undone

# List undone English lessons with details
make list-undone-en

# List undone Kiswahili lessons with details
make list-undone-sw
```

### 4. Process Lessons with Claude Code

#### Individual Lesson Processing
```bash
# Process a single lesson (English)
/cleanup-lessons 1888 Q1

# Process with translation to Kiswahili
/cleanup-lessons 1888 Q1 sw

# Process a range of lessons
/cleanup-lessons 1888 Q1 --end-year 1890 --end-quarter Q2

# Redo existing processing
/cleanup-lessons 1888 Q1 --redo
```

#### Batch Processing with AI
```bash
# Process all undone English lessons from first undone (AI does OCR cleanup)
/cleanup en

# Process all undone Kiswahili lessons from first undone (AI translates)
/cleanup sw

# Process up to a specific year with parallel processing
/cleanup en --end-year 1895

# Find first undone lesson with source files available
make first-not-done-en
```

#### Page-by-Page Processing (New! For PDF Sources)
```bash
# Extract lesson from PDF page text files (better OCR control)
/extract-from-pages 1913 Q2

# Extract with translation to Kiswahili
/extract-from-pages 1913 Q2 sw

# Redo extraction with improvements
/extract-from-pages 1913 Q2 --redo
```

**AI-Powered Processing Features:**
- AI performs OCR cleanup and markdown formatting directly
- Up to 4 parallel agents for full year processing (Q1-Q4)
- Intelligent source file validation and dependency checking
- Page-by-page processing for superior OCR error handling
- Automatic progress tracking and status updates

## Features

### OCR Cleanup and Formatting
- Automatic OCR error correction
- Convert roman numerals to arabic (LESSON IV → Lesson 4)
- Fix ALL CAPS formatting to proper case
- Ensure double spacing between questions/notes for PDF rendering
- Create properly structured markdown files

### Translation Workflow
- Process English lessons first
- Translate to Kiswahili with preserved formatting
- Maintain theological accuracy and cultural appropriateness
- Auto-update completion status

### Progress Tracking
- Track completion by language
- Generate progress reports
- List undone lessons by year range
- Monitor processing status

### Directory Organization
- Automatic decade/year/quarter structure
- Language-specific folders (en, sw, etc.)
- Consistent file naming conventions

## Claude Commands

### `/cleanup-lessons`
Individual lesson processing with OCR cleanup and translation.

**Syntax:**
```
/cleanup-lessons YEAR QUARTER [LANGUAGE] [OPTIONS]
```

**Examples:**
```bash
/cleanup-lessons 1888 Q1                    # Process 1888 Q1 in English
/cleanup-lessons 1888 Q1 sw                 # Process 1888 Q1 in Kiswahili
/cleanup-lessons 1888 Q1 --end-year 1890    # Process range
/cleanup-lessons 1888 Q1 --redo             # Redo processing
```

**Options:**
- `--redo` - Reprocess even if already done
- `--end-year YEAR` - Process range to end year
- `--end-quarter QUARTER` - Process range to end quarter

### `/cleanup` (AI-Powered Batch Processing)
AI-driven batch processing starting from first undone lesson with source files.

**Syntax:**
```
/cleanup LANGUAGE [OPTIONS]
```

**Examples:**
```bash
/cleanup en                     # Process all undone English lessons with AI
/cleanup sw                     # Process Kiswahili translations with AI
/cleanup en --end-year 1895     # Process English up to 1895
```

**Options:**
- `--end-year YEAR` - Stop processing at specified year
- `--end-quarter QUARTER` - Stop processing at specified quarter

### `/extract-from-pages` (Page-by-Page Processing)
Extract and organize lesson content from PDF page text files for superior OCR control.

**Syntax:**
```
/extract-from-pages YEAR QUARTER [LANGUAGE] [OPTIONS]
```

**Examples:**
```bash
/extract-from-pages 1913 Q2     # Extract from PDF page files
/extract-from-pages 1913 Q2 sw  # Extract and translate to Kiswahili
/extract-from-pages 1913 Q2 --redo  # Redo extraction
```

**Options:**
- `--redo` - Redo extraction even if already done

**Page Processing Features:**
- **Page-by-Page Control**: Process individual pages for better error handling
- **Smart Content Reconstruction**: Intelligently merge content across pages
- **Superior OCR Correction**: Fix errors with page-level context
- **Content Mapping**: Track which content comes from which pages
- **Quality Assessment**: Monitor OCR quality page by page

**AI Features (Both Commands):**
- **Direct OCR Cleanup**: AI performs all text correction and formatting
- **Parallel Processing**: Up to 4 agents processing quarters simultaneously
- **Smart Dependencies**: Automatic English version checking for translations
- **Source Validation**: Only processes lessons with available source files
- **Progress Tracking**: Automatic status updates and completion tracking

## Scripts

### Download Lessons
```bash
python scripts/download-lessons.py [--test] [--dry-run]
```

### Update Lesson Status
```bash
# Add language completion
python scripts/update-lessons-json.py add 1888 Q1 en

# Remove language completion
python scripts/update-lessons-json.py remove 1888 Q1 sw

# Check lesson status
python scripts/update-lessons-json.py status 1888 Q1

# List all languages
python scripts/update-lessons-json.py languages
```

### List Progress
```bash
# List all undone lessons
python scripts/list-undone-lessons.py

# List undone for specific language
python scripts/list-undone-lessons.py --language sw

# List completed lessons
python scripts/list-undone-lessons.py --completed

# Show progress for all languages
python scripts/list-undone-lessons.py --progress

# Filter by year range
python scripts/list-undone-lessons.py --start-year 1888 --end-year 1895
```

## Quality Standards

### OCR Cleanup Requirements
- [ ] All OCR errors corrected
- [ ] Roman numerals converted to arabic numbers
- [ ] ALL CAPS converted to proper case
- [ ] **Double spacing between question/note numbers**
- [ ] Proper markdown syntax
- [ ] Original theological content preserved

### File Structure Requirements
- [ ] Proper decade/year/quarter/language directory structure
- [ ] Consistent file naming (front-matter.md, week-01.md, etc.)
- [ ] Valid JSON metadata in contents.json
- [ ] PDF rendering compatibility

### Translation Standards
- [ ] English version completed first
- [ ] Theological accuracy maintained
- [ ] Cultural appropriateness for target language
- [ ] Consistent terminology usage

## Makefile Targets

| Target | Description |
|--------|-------------|
| `help` | Show available targets |
| `download-lessons` | Download all lessons |
| `download-test` | Test with first 10 files |
| `list-progress` | Show completion progress |
| `list-undone` | List undone lessons |
| `list-undone-en` | List undone English lessons |
| `list-undone-sw` | List undone Kiswahili lessons |
| `first-not-done-en` | Show first undone English lesson |
| `first-not-done-sw` | Show first undone Kiswahili lesson |
| `show-languages` | List all available languages |
| `clean` | Remove downloaded files |

## Development Workflow

### Standard Processing Cycle
1. **Download raw lessons**: `make download-lessons`
2. **Check progress**: `make list-progress`
3. **Process English**: `/cleanup-lessons YEAR QUARTER`
4. **Process translation**: `/cleanup-lessons YEAR QUARTER sw`
5. **Verify completion**: `make list-completed-en`

### Quality Assurance
1. **Process with validation**: `/cleanup-lessons YEAR QUARTER`
2. **Review generated files**: Check markdown structure
3. **Re-process if needed**: `/cleanup-lessons YEAR QUARTER --redo`
4. **Update metadata**: Automatic via Claude command

## Contributing

1. Follow the established directory structure
2. Ensure double spacing for PDF compatibility
3. Preserve original theological content
4. Test with small batches before full processing
5. Update completion status after processing

## License

This project is for processing historical Sabbath School lessons for preservation and accessibility.