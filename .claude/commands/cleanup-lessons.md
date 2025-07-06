# Cleanup Lessons

Clean up OCR errors in Sabbath School lesson text files and convert them into properly formatted markdown files with optional translation to Kiswahili.

## Target: $ARGUMENTS

Expected format: `YEAR QUARTER [LANGUAGE] [--redo] [--end-year YEAR] [--end-quarter QUARTER]`

Examples:
- `1888 Q1` - Process 1888 Q1 in English
- `1888 Q1 sw` - Process 1888 Q1 in Kiswahili
- `1888 Q1 --end-year 1890 --end-quarter Q2` - Process range from 1888 Q1 to 1890 Q2
- `1888 Q1 --redo` - Redo processing even if already done

## Processing Workflow

1. **Parse Arguments**
   - Extract start year and quarter from $ARGUMENTS
   - Parse optional end year/quarter for range processing
   - Determine target language (default: en)
   - Check for --redo flag to override existing work
   - Validate arguments and ensure proper format

2. **ULTRATHINK**
   - Create comprehensive processing strategy using TodoWrite tool
   - Analyze the scope of lessons to be processed
   - Plan the OCR cleanup and formatting approach
   - Determine translation requirements if target language is not English
   - Validate that source files exist and are accessible
   - Plan double spacing validation for PDF rendering requirements

3. **Load Lesson Metadata**
   - Read data/lessons.json to get lesson information
   - Find matching lessons for the specified year(s) and quarter(s)
   - Extract lesson metadata: title, type (quarterly/biannual), expected weeks
   - Validate that lessons exist in the metadata
   - Check current completion status for target language

4. **Locate Source Files**
   - Check for source files in data/downloads/[DECADE]/[YEAR]/[QUARTER]/
   - Verify that lesson text files exist (lesson_01.txt, lesson_02.txt, etc.)
   - If source files don't exist, check data/lessons/ structure
   - Report missing files and exit if critical files are unavailable

5. **Process Each Lesson**
   For each lesson in the specified range:
   
   ### 5.1 Setup Lesson Context
   - Create lesson processing context with metadata
   - Determine output directory: data/lessons/[DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/
   - Check if lesson already processed (skip unless --redo specified)
   - Load source text file content

   ### 5.2 OCR Cleanup and Formatting (Good OCR Fixing Bad OCR)
   Apply comprehensive OCR cleanup based on claude-code-prompt-template.md:
   
   **Critical Understanding**: The original printed text is perfect. We are acting as a "good OCR" to correct the mistakes made by the "bad OCR" that digitized the text. Our goal is to restore the original printed text exactly as it appeared.
   
   **OCR Error Correction:**
   - Restore the original printed text by correcting OCR digitization errors
   - Fix common OCR issues: l/I confusion, rn/m confusion, cl/d confusion, character misrecognition
   - Restore original theological terminology and biblical references to their printed form
   - Do NOT change author content - only fix OCR digitization mistakes
   - Correct punctuation errors, number recognition errors, and word splitting errors
   
   **Formatting Changes:**
   - Convert roman numerals to arabic numerals for lesson numbers (LESSON IV → Lesson 4)
   - Convert ALL CAPS words at beginning of paragraphs to proper case
   - Fix broken paragraph lines where text was incorrectly split
   - Format dates consistently (April 6, 1901)
   
   **Markdown Structure:**
   - Use # for lesson titles (H1)
   - Use ## for section headings (H2)
   - Create proper markdown tables for tabular content
   - Use ## Notes as heading for notes sections
   - Format paragraphs correctly without unwanted line breaks
   
   **Critical: Double Spacing Validation**
   - Ensure double spacing between different question numbers
   - Ensure double spacing between different note numbers
   - This is essential for proper PDF rendering
   - Validate spacing patterns before finalizing files

   ### 5.3 File Organization
   Create properly structured markdown files:
   - **front-matter.md**: Everything before the first lesson
   - **week-01.md, week-02.md, etc.**: Each weekly lesson (zero-padded numbers)
   - **back-matter.md**: Everything after the last lesson
   - **contents.json**: Lesson metadata and structure information
   
   File naming: `data/lessons/[DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/[filename].md`

6. **Translation Workflow (if target language is not English)**
   - Verify English version is completed and properly formatted
   - Load English markdown files as source for translation
   - Translate content to target language (Kiswahili)
   - Preserve markdown formatting and structure
   - Maintain biblical references and theological terminology accuracy
   - Ensure cultural appropriateness for target language

7. **Quality Validation**
   Before completing each lesson, verify:
   - [ ] All OCR errors corrected
   - [ ] Roman numerals converted to arabic numbers
   - [ ] ALL CAPS converted to proper case where appropriate
   - [ ] Paragraph breaks are logical and correct
   - [ ] Tables properly formatted in markdown
   - [ ] Dates follow consistent format
   - [ ] **Double spacing between question/note numbers validated**
   - [ ] Original theological content preserved
   - [ ] Proper markdown syntax used throughout
   - [ ] All expected weekly files created
   - [ ] File names follow exact convention

8. **Update Lesson Metadata**
   - Update data/lessons.json to mark language as completed
   - Add completion timestamp and processing notes
   - Update language availability for the processed lessons
   - Validate JSON structure and save changes

9. **Generate Processing Report**
   - Summary of lessons processed
   - List of files created/updated
   - Any issues encountered during processing
   - Quality validation results
   - Next steps or recommended actions

## Advanced Features

### Range Processing
```bash
# Process multiple lessons in sequence
/cleanup-lessons 1888 Q1 --end-year 1890 --end-quarter Q2

# Process entire year
/cleanup-lessons 1888 Q1 --end-year 1888 --end-quarter Q4
```

### Language Options
```bash
# Process English (default)
/cleanup-lessons 1888 Q1

# Process Kiswahili translation
/cleanup-lessons 1888 Q1 sw

# Process with redo flag
/cleanup-lessons 1888 Q1 sw --redo
```

### Biannual Quarter Handling
- Automatically handle Q1-Q2 format lessons
- Convert biannual quarters to appropriate structure
- Process extended lesson content properly

## Error Handling

### Common Issues and Solutions
- **Source Files Missing**: Guide user to download lessons first
- **Invalid Year/Quarter**: Validate against lessons.json metadata
- **Already Processed**: Skip unless --redo flag specified
- **Translation Dependencies**: Ensure English version exists before translation
- **Validation Failures**: Report specific quality issues and requirements

## Integration with Development Workflow

### Standard Processing Cycle
```bash
# 1. Process English version first
/cleanup-lessons 1888 Q1

# 2. Process translation to Kiswahili
/cleanup-lessons 1888 Q1 sw

# 3. Process range of lessons
/cleanup-lessons 1888 Q1 --end-year 1890 --end-quarter Q4
```

### Quality Assurance Workflow
```bash
# 1. Process with quality validation
/cleanup-lessons 1888 Q1

# 2. Review generated markdown files
# 3. Re-process if issues found
/cleanup-lessons 1888 Q1 --redo

# 4. Process translation
/cleanup-lessons 1888 Q1 sw
```

## Completion Criteria

Processing operation is complete when:
- [ ] All specified lessons processed according to quality standards
- [ ] OCR cleanup applied comprehensively with proper formatting
- [ ] **Double spacing validated between question/note numbers**
- [ ] Markdown files created with proper structure and naming
- [ ] Translation completed if target language specified
- [ ] data/lessons.json updated with completion status
- [ ] Processing report generated with summary and next steps
- [ ] All files validated for PDF rendering compatibility

## Dependencies

### Required Scripts
- `scripts/update-lessons-json.py` - For updating lesson completion status
- `scripts/list-undone-lessons.py` - For progress tracking

### File Structure Requirements
```
data/
├── lessons.json              # Lesson metadata
├── downloads/               # Downloaded source files
│   └── [DECADE]/[YEAR]/[QUARTER]/lesson_*.txt
└── lessons/                 # Processed markdown files
    └── [DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/
        ├── front-matter.md
        ├── week-01.md
        ├── week-02.md
        ├── ...
        ├── back-matter.md
        └── contents.json
```

This command provides comprehensive lesson processing with quality validation, translation support, and proper metadata management for the Sabbath School lessons project.