# Extract From Pages

Extract and organize lesson content from page-by-page text files created from PDF conversion. This command processes individual page text files to create structured markdown lessons.

## Target: $ARGUMENTS

Expected format: `YEAR QUARTER [LANGUAGE] [--redo]`

Examples:
- `1913 Q2` - Extract 1913 Q2 lesson from page files
- `1888 Q1 sw` - Extract and translate 1888 Q1 to Kiswahili
- `1914 Q1 --redo` - Redo extraction even if already done

## Processing Workflow

1. **Parse Arguments and Setup**
   - Extract year, quarter, and optional language from $ARGUMENTS
   - Validate that source page files exist in data/pdfs/
   - Set up output directory structure in data/lessons/
   - Check for --redo flag to override existing work

2. **ULTRATHINK**
   - Create comprehensive page-by-page extraction strategy using TodoWrite tool
   - Analyze the scope and structure of available page files
   - Plan content identification and organization approach
   - Determine lesson boundaries and weekly divisions
   - Plan translation workflow if target language is not English

3. **Locate and Load Page Files**
   - Find page text files in `data/pdfs/[DECADE]/[YEAR]/[QUARTER]/lesson_*_pages/`
   - Load conversion metadata to understand extraction method used
   - Read all page text files in sequence (page_001.txt, page_002.txt, etc.)
   - Analyze page content quality and OCR accuracy

4. **Content Analysis and Structure Identification**
   
   ### 4.1 Page Content Analysis
   - Examine each page for content type (title page, lesson content, exercises, etc.)
   - Identify lesson boundaries and week divisions
   - Detect headers, section breaks, and content structure
   - Recognize question/answer sections, notes, and references

   ### 4.2 Lesson Structure Detection
   - **Front Matter**: Title pages, introductions, table of contents
   - **Weekly Lessons**: Individual lesson content with consistent structure
   - **Back Matter**: Appendices, notes, conclusion materials
   - **Study Aids**: Questions, exercises, memory verses, references

5. **OCR Cleanup and Content Restoration (Good OCR Fixing Bad OCR)**
   
   **Critical Understanding**: The original printed text is perfect. We are acting as a "good OCR" to correct the mistakes made by the OCR process that converted the PDF pages to text.

   ### 5.1 Page-Level OCR Correction
   - **Fix character recognition errors**: l/I confusion, rn/m confusion, cl/d confusion
   - **Restore broken words**: Words split across lines or incorrectly recognized
   - **Correct punctuation**: Fix misread periods, commas, quotation marks
   - **Fix number recognition**: Dates, verse numbers, page numbers, lesson numbers
   - **Restore proper spacing**: Fix spacing issues and paragraph breaks

   ### 5.2 Content Reconstruction
   - **Merge split content**: Combine content split across pages properly
   - **Restore formatting**: Headers, subheaders, lists, and structure
   - **Fix page headers/footers**: Remove or properly handle page navigation elements
   - **Restore biblical references**: Ensure scripture citations are accurate
   - **Maintain theological terminology**: Preserve doctrinal terms exactly

6. **Content Organization and File Creation**
   
   ### 6.1 Content Segmentation
   - **Identify week boundaries**: Recognize where each weekly lesson begins/ends
   - **Extract front matter**: Title page, introduction, preface content
   - **Separate weekly content**: Individual lessons with consistent structure
   - **Gather back matter**: Appendices, notes, conclusion content

   ### 6.2 Markdown File Creation
   Create properly structured files in `data/lessons/[DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/`:
   
   **Required Files:**
   - `front-matter.md`: Title, introduction, preface from initial pages
   - `week-01.md` through `week-XX.md`: Individual weekly lessons (zero-padded)
   - `back-matter.md`: Appendices, notes, conclusion from final pages
   - `contents.json`: Metadata with lesson structure and page mapping

   ### 6.3 Markdown Formatting
   - **Headers**: Use # for lesson titles, ## for major sections, ### for subsections
   - **Questions and Notes**: Ensure **double spacing between different question numbers and note numbers** (critical for PDF rendering)
   - **Tables**: Convert tabular content to proper markdown tables
   - **Lists**: Format numbered and bulleted lists correctly
   - **Biblical References**: Format scripture citations consistently
   - **Memory Verses**: Highlight and format memory verses appropriately

7. **Quality Validation and Content Verification**
   
   ### 7.1 Content Completeness Check
   - Verify all pages were processed and no content lost
   - Check that lesson structure makes sense chronologically
   - Ensure all weeks are accounted for based on lesson metadata
   - Validate that no pages were skipped or duplicated

   ### 7.2 OCR Quality Validation
   - [ ] All page-level OCR errors corrected - original printed text restored
   - [ ] Roman numerals converted to arabic numbers consistently  
   - [ ] ALL CAPS converted to proper case where appropriate
   - [ ] **Double spacing between question numbers validated** (e.g., Question 1\n\n[content]\n\nQuestion 2)
   - [ ] **Double spacing between note numbers validated** (e.g., Note 1\n\n[content]\n\nNote 2)
   - [ ] Paragraph breaks logical and consistent with original layout
   - [ ] Markdown syntax correct and properly formatted
   - [ ] Biblical references and theological terms restored to original form
   - [ ] Page headers/footers properly handled or removed

8. **Translation Workflow (For Non-English Languages)**
   
   When target language is not English:
   
   ### 8.1 English Base Verification
   - Ensure English version is completed first from page extraction
   - Load English markdown files as translation source
   - Validate English content structure and completeness

   ### 8.2 Translation Process
   - Translate content while preserving markdown formatting
   - Maintain biblical references in appropriate language tradition
   - Ensure theological accuracy and cultural appropriateness
   - Preserve lesson structure, questions, and study aids
   - Keep cross-references and memory verses consistent

9. **Progress Tracking and Metadata Updates**
   - Create detailed processing log with page-by-page results
   - Update `data/lessons.json` with completion status using:
     `python scripts/update-lessons-json.py add [YEAR] [QUARTER] [LANGUAGE]`
   - Document any issues or quality concerns found
   - Record page mapping and content organization decisions

10. **Final Validation and Reporting**
    - Verify all required markdown files created with proper content
    - Confirm proper directory structure and file naming
    - Validate **double spacing for PDF rendering compatibility**
    - Generate comprehensive extraction report with:
      - Pages processed successfully
      - Content organization decisions
      - Quality issues identified and resolved
      - Translation status (if applicable)

## Example Processing Scenarios

### English Extraction from PDF Pages
```bash
# Extract 1913 Q2 lesson from converted PDF pages
/extract-from-pages 1913 Q2

# Redo extraction with improvements
/extract-from-pages 1913 Q2 --redo
```

**Page Processing Flow:**
1. Load pages from `data/pdfs/1910s/1913/q2/lesson_02_pages/page_*.txt`
2. Analyze page content and identify lesson structure
3. Apply OCR correction and content restoration
4. Create structured markdown files in `data/lessons/1910s/1913/q2/en/`

### Translation Extraction
```bash
# Extract and translate to Kiswahili (requires English base)
/extract-from-pages 1913 Q2 sw
```

**Translation Dependencies:**
- Automatically checks for completed English version
- Uses English markdown as translation source
- Maintains parallel structure in target language

## Advanced Features

### Page-by-Page Processing Benefits
- **Better Error Handling**: Identify exactly which pages have issues
- **Granular Control**: Process specific page ranges if needed
- **Quality Tracking**: Monitor OCR quality page by page
- **Content Mapping**: Track which content comes from which pages

### Content Reconstruction Intelligence
- **Smart Merging**: Intelligently combine content split across pages
- **Structure Recognition**: Automatically detect lesson boundaries
- **Format Preservation**: Maintain original formatting intent
- **Error Isolation**: Handle OCR errors without losing entire lessons

## Error Handling and Recovery

### Page-Level Error Management
- **Missing Pages**: Detect and report gaps in page sequence
- **Poor OCR Quality**: Identify pages needing manual review
- **Content Boundaries**: Handle lessons that span unexpected page ranges
- **Format Issues**: Gracefully handle non-standard page layouts

### Recovery Mechanisms
- **Page Mapping**: Track which pages contribute to which content
- **Quality Scoring**: Assess OCR quality per page
- **Manual Review Flags**: Mark pages needing human attention
- **Incremental Processing**: Process successfully extracted content even if some pages fail

## Integration with PDF Workflow

### Pre-Processing Steps
```bash
# Download PDFs
make download-pdfs

# Convert PDFs to page text files
make convert-pdfs

# Extract lessons from pages
/extract-from-pages 1913 Q2
```

### Post-Processing Verification
```bash
# Check extraction results
make list-progress

# Verify specific extraction
python scripts/update-lessons-json.py status 1913 Q2
```

## Completion Criteria

Page extraction operation is complete when:
- [ ] All available page text files processed successfully
- [ ] Content properly organized into front-matter, weekly lessons, back-matter
- [ ] **Double spacing validated between questions and notes for PDF compatibility**
- [ ] OCR errors corrected - original printed text accurately restored
- [ ] No author content changed - only OCR errors fixed
- [ ] Proper markdown structure created with all required files
- [ ] Translation completed if target language specified
- [ ] lessons.json updated with completion status
- [ ] Processing report generated with page mapping and quality assessment

## File Structure Requirements

### Input (Page Text Files)
```
data/pdfs/
└── [DECADE]/[YEAR]/[QUARTER]/
    └── lesson_XX_pages/
        ├── page_001.txt
        ├── page_002.txt
        ├── ...
        └── conversion_metadata.json
```

### Output (Structured Lessons)
```
data/lessons/
└── [DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/
    ├── front-matter.md      # Title, introduction, preface
    ├── week-01.md          # First weekly lesson
    ├── week-02.md          # Second weekly lesson
    ├── ...                 # Additional weeks as needed
    ├── back-matter.md      # Appendices, conclusion
    └── contents.json       # Lesson metadata and page mapping
```

### Dependencies
- `scripts/update-lessons-json.py` - For updating completion status
- `data/lessons.json` - Lesson metadata and completion tracking
- Page text files from PDF conversion process

This command provides intelligent page-by-page content extraction with superior OCR error handling, content reconstruction, and quality validation for reliable lesson processing from PDF sources.