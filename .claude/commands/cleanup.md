# Cleanup

Batch process lessons starting from the first undone lesson for a specified language and continue until all lessons are processed. The AI performs all OCR cleanup and markdown formatting directly.

## Target: $ARGUMENTS

Expected format: `LANGUAGE [--end-year YEAR] [--end-quarter QUARTER]`

Examples:
- `en` - Process all undone English lessons starting from first undone
- `sw` - Process all undone Kiswahili lessons starting from first undone  
- `en --end-year 1895` - Process English lessons up to 1895
- `sw --end-quarter Q2` - Process Kiswahili lessons up to Q2 of current processing

## Processing Workflow

1. **Parse Arguments and Setup**
   - Extract target language from $ARGUMENTS
   - Parse optional end year/quarter for processing limits
   - Validate language code (en, sw, etc.)
   - Set processing boundaries and scope

2. **ULTRATHINK**
   - Create comprehensive batch processing strategy using TodoWrite tool
   - Analyze the scope of lessons to be processed sequentially
   - Plan efficient processing order (chronological by year, then quarter)
   - Determine translation dependencies (English first for translations)
   - Plan parallel processing: up to 4 agents for full year (Q1-Q4) or remaining quarters

3. **Find Starting Point and Scope**
   - Use `python scripts/list-undone-lessons.py --language [LANG] --first-undone` to find first undone lesson with source files
   - Determine processing scope based on start point and optional end limits
   - Group lessons by year for parallel processing
   - Validate that all lessons in scope have source files in data/downloads/

4. **Parallel Processing Strategy**
   - **Full Year Processing**: If starting from Q1, launch 4 agents in parallel for Q1, Q2, Q3, Q4
   - **Partial Year Processing**: If starting mid-year (Q2, Q3, Q4), process remaining quarters in parallel
   - **Sequential Year Processing**: Complete one year before moving to next
   - Each agent handles one quarter independently

5. **Source File Location and Validation**
   For each lesson to be processed:
   - Check source files in `data/downloads/[DECADE]/[YEAR]/[QUARTER]/lesson_*.txt`
   - For translations: verify English version exists in `data/lessons/[DECADE]/[YEAR]/[QUARTER]/en/`
   - Load lesson metadata from `data/lessons.json`
   - Validate lesson structure and source content availability

6. **OCR Cleanup and Formatting (Per Lesson)**
   
   The AI performs all cleanup directly without scripts:

   ### 6.1 Load and Analyze Source Content
   - Read source text file(s) from data/downloads/
   - Identify lesson structure, weeks, and content sections
   - Analyze OCR quality and common error patterns
   - Plan content organization and file splitting

   ### 6.2 OCR Error Correction (Good OCR Fixing Bad OCR)
   
   **Critical Understanding**: The original printed text is perfect. We are acting as a "good OCR" to correct the mistakes made by the "bad OCR" that digitized the text. Our goal is to restore the original printed text exactly as it appeared.
   
   Apply comprehensive OCR error correction:
   - **Fix character recognition errors**: l/I confusion, rn/m confusion, cl/d confusion, special characters
   - **Restore original text**: Correct OCR mistakes to match what was actually printed originally
   - **Never change content**: Only fix digitization errors - never alter the original author's words
   - **Maintain theological terminology**: Restore biblical references and doctrinal terms to their original printed form
   - **Fix broken words and spacing**: Correct words that OCR incorrectly split across lines
   - **Restore punctuation**: Fix OCR misreading of periods, commas, quotation marks
   - **Correct number recognition**: Fix OCR errors in dates, verse numbers, page numbers

   ### 6.3 Formatting Standardization
   - **Convert roman numerals to arabic**: "LESSON IV" → "Lesson 4", "QUESTION II" → "Question 2"
   - **Fix ALL CAPS formatting**: Convert inappropriate ALL CAPS to proper case
   - **Standardize dates**: Format consistently as "Month Day, Year" (e.g., "April 6, 1901")
   - **Fix paragraph breaks**: Repair text incorrectly split across lines
   - **Preserve intentional formatting**: Keep emphases, quotes, and structured content

   ### 6.4 Markdown Structure Creation
   - **Headers**: Use # for lesson titles, ## for major sections, ### for subsections
   - **Questions and Notes**: Ensure **double spacing between different question numbers and note numbers** (critical for PDF rendering)
   - **Tables**: Convert tabular content to proper markdown tables
   - **Lists**: Format numbered and bulleted lists correctly
   - **Emphasis**: Use **bold** and *italic* appropriately for theological emphasis

   ### 6.5 File Organization and Creation
   Create properly structured files in `data/lessons/[DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/`:
   
   **Required Files:**
   - `front-matter.md`: Title page, introduction, preface content
   - `week-01.md` through `week-XX.md`: Individual weekly lessons (zero-padded)
   - `back-matter.md`: Appendices, notes, conclusion content
   - `contents.json`: Metadata with lesson structure and week information

   **Content Organization:**
   - Split content logically by weeks based on lesson structure
   - Maintain theological flow and lesson progression
   - Preserve cross-references and study aids
   - Include all original study questions and memory verses

   ### 6.6 Quality Validation (Critical)
   Before finalizing each lesson:
   - [ ] All OCR digitization errors corrected - original printed text restored accurately
   - [ ] Roman numerals converted to arabic numbers consistently
   - [ ] ALL CAPS converted to proper case where appropriate
   - [ ] **Double spacing between question numbers validated** (e.g., Question 1\n\n[content]\n\nQuestion 2)
   - [ ] **Double spacing between note numbers validated** (e.g., Note 1\n\n[content]\n\nNote 2)
   - [ ] Paragraph breaks logical and consistent with original printed layout
   - [ ] Markdown syntax correct and properly formatted
   - [ ] All expected weekly files created with proper naming
   - [ ] Original printed text content restored exactly - no author content changed
   - [ ] Biblical references and theological terms match original printed form
   - [ ] Dates, numbers, and proper names correctly restored from OCR errors

7. **Translation Workflow (For Non-English Languages)**
   
   When target language is not English:
   
   ### 7.1 English Dependency Check
   - Verify English version completed and properly formatted
   - Load English markdown files as translation source
   - Ensure all required English files present

   ### 7.2 Translation Process
   - Translate content while preserving markdown formatting
   - Maintain biblical references in appropriate language tradition
   - Ensure theological accuracy and cultural appropriateness
   - Preserve lesson structure, questions, and study aids
   - Keep cross-references and memory verses consistent

   ### 7.3 Language-Specific Considerations
   - **Kiswahili (sw)**: Use appropriate biblical terminology and cultural context
   - **Luo**: Maintain cultural and linguistic appropriateness
   - Preserve emphasis and theological concepts accurately
   - Adapt examples while maintaining doctrinal integrity

8. **Progress Tracking and Status Updates**
   - Update `data/lessons.json` with completion status using:
     `python scripts/update-lessons-json.py add [YEAR] [QUARTER] [LANGUAGE]`
   - Log processing results for each lesson
   - Report any issues or missing content
   - Maintain processing statistics

9. **Parallel Processing Coordination**
   - Launch multiple Task agents for parallel quarter processing
   - Coordinate to avoid conflicts and ensure proper sequencing
   - Monitor progress across all parallel processes
   - Handle errors in individual processes without stopping others

10. **Final Validation and Reporting**
    - Verify all processed lessons meet quality standards
    - Confirm proper directory structure and file naming
    - Validate **double spacing for PDF rendering compatibility**
    - Generate comprehensive processing report
    - Update progress tracking and recommend next steps

## Example Processing Scenarios

### English Processing (Direct from Source Files)
```bash
# Process all undone English lessons starting from first with source files
/cleanup en

# Process English lessons up to specific year
/cleanup en --end-year 1900

# Process remaining quarters of current year
/cleanup en --end-quarter Q4
```

**Parallel Processing Example:**
- Starting from 1913 Q2: Launches agents for Q2, Q3, Q4 (3 agents)
- Starting from 1914 Q1: Launches agents for Q1, Q2, Q3, Q4 (4 agents)
- Completes one year before proceeding to next year

### Translation Processing (Requires English Base)
```bash
# Process Kiswahili translations (after English is completed)
/cleanup sw

# Process limited range of translations
/cleanup sw --end-year 1895
```

**Translation Dependencies:**
- Automatically checks for completed English version
- Loads English markdown files as translation source
- Maintains parallel file structure in target language

## Processing Coordination

### Parallel Agent Management
- **Task Distribution**: Each agent processes one quarter independently
- **Conflict Avoidance**: Agents work on different quarters simultaneously
- **Progress Synchronization**: Central tracking of completion status
- **Error Isolation**: Individual agent failures don't stop other processes

### Quality Assurance Across Agents
- Consistent OCR cleanup standards across all parallel processes
- Uniform markdown formatting and structure
- **Critical**: Double spacing validation for PDF compatibility
- Cross-agent progress reporting and status updates

## Error Handling and Recovery

### Robust Processing
- **Missing Source Files**: Skip lesson, log issue, continue with next available
- **Translation Dependencies**: Clear reporting of missing English prerequisites
- **OCR Failures**: Detailed error logging with specific lesson information
- **File System Issues**: Graceful handling with recovery suggestions

### Progress Preservation
- Automatic status updates to lessons.json after each lesson completion
- Resume capability from last successful lesson
- Detailed processing logs for troubleshooting and quality review

## Integration with Project Workflow

### Pre-Processing Steps
```bash
# Check what needs to be processed
make first-not-done-en

# Review available source files
make list-undone-en-with-source

# Start batch processing
/cleanup en
```

### Post-Processing Verification
```bash
# Check updated progress
make list-progress

# Verify specific completions
python scripts/update-lessons-json.py status 1913 Q2
```

## Completion Criteria

Batch processing operation is complete when:
- [ ] All undone lessons with source files processed for target language
- [ ] **Double spacing validated between questions and notes for PDF compatibility**
- [ ] OCR error correction completed - original printed text accurately restored
- [ ] No author content changed - only OCR digitization errors fixed
- [ ] Translation dependencies satisfied and validated (for non-English)
- [ ] lessons.json updated with completion status for all processed lessons
- [ ] Proper file structure created with all required markdown files
- [ ] Comprehensive processing report generated with statistics and issues
- [ ] Parallel processing coordination completed successfully

## File Structure Requirements

### Source Files (Input)
```
data/downloads/
└── [DECADE]/[YEAR]/[QUARTER]/
    ├── lesson_01.txt
    ├── lesson_02.txt
    └── ...
```

### Processed Files (Output)
```
data/lessons/
└── [DECADE]/[YEAR]/[QUARTER]/[LANGUAGE]/
    ├── front-matter.md      # Title, introduction, preface
    ├── week-01.md          # First weekly lesson
    ├── week-02.md          # Second weekly lesson
    ├── ...                 # Additional weeks as needed
    ├── back-matter.md      # Appendices, conclusion
    └── contents.json       # Lesson metadata and structure
```

### Dependencies
- `scripts/list-undone-lessons.py` - Finding first undone lesson with source files
- `scripts/update-lessons-json.py` - Updating completion status
- `data/lessons.json` - Lesson metadata and completion tracking

This command provides comprehensive AI-driven lesson processing with parallel execution, quality validation, and intelligent progress management for efficient large-scale OCR cleanup and formatting workflows.