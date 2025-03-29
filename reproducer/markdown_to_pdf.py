#!/usr/bin/env python3
"""
Sabbath School Lesson Markdown to PDF Converter

This script converts markdown files containing Sabbath School lessons
into beautifully formatted PDFs with a consistent design.

Requirements:
- Python 3.6+
- pip install markdown weasyprint python-frontmatter beautifulsoup4

Usage:
python3 sabbath_school_converter.py input_markdown.md output.pdf
"""

import os
import re
import sys
import argparse
import logging
import markdown
import frontmatter
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('sabbath_school_converter')

# CSS for styling the PDF output
CSS_TEMPLATE = """
@page {
    size: letter;
    margin: 0.75in;
    @bottom-center {
        content: counter(page);
        font-family: Georgia, serif;
        font-size: 12pt;
        color: #5a4130;
    }
    @bottom-left {
        content: "Gospel Sounder - Q1 2025";
        font-family: Georgia, serif;
        font-size: 10pt;
        color: #5a4130;
    }
    @bottom-right {
        content: "Old Testament History";
        font-family: Georgia, serif;
        font-size: 10pt;
        color: #5a4130;
    }
}

body {
    font-family: Georgia, serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #3c1815;
}

.lesson-header {
    background-color: #f5f1e6;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #8b4513;
    position: relative;
    height: 100px;
}

.lesson-circle {
    position: absolute;
    top: 20px;
    left: 20px;
    width: 80px;
    height: 80px;
    background-color: #e0d5c0;
    border: 2px solid #8b4513;
    border-radius: 50%;
    text-align: center;
    line-height: 80px;
    font-size: 40px;
    font-weight: bold;
    color: #3c1815;
}

.lesson-title {
    position: absolute;
    top: 20px;
    left: 120px;
    font-size: 24pt;
    font-weight: bold;
    color: #3c1815;
}

.lesson-date {
    position: absolute;
    top: 60px;
    left: 120px;
    font-size: 14pt;
    color: #5a4130;
}

.corner {
    position: absolute;
    width: 15px;
    height: 15px;
    background-color: #8b4513;
}

.top-left {
    top: 0;
    left: 0;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    border-bottom-left-radius: 10px;
}

.top-right {
    top: 0;
    right: 0;
    border-top-left-radius: 10px;
    border-bottom-right-radius: 10px;
    border-bottom-left-radius: 10px;
}

.bottom-left {
    bottom: 0;
    left: 0;
    border-top-right-radius: 10px;
    border-top-left-radius: 10px;
    border-bottom-right-radius: 10px;
}

.bottom-right {
    bottom: 0;
    right: 0;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    border-bottom-left-radius: 10px;
}

.questions-section {
    border: 1px solid #8b4513;
    padding: 20px;
    margin-bottom: 20px;
}

.questions-header {
    font-size: 14pt;
    font-weight: bold;
    margin-bottom: 10px;
    border-bottom: 1px solid #8b4513;
    padding-bottom: 5px;
}

.question {
    margin-bottom: 15px;
}

.question-number {
    font-weight: bold;
    float: left;
    width: 25px;
}

.question-text {
    margin-left: 25px;
}

.scripture-ref {
    float: right;
    color: #5a4130;
    font-style: italic;
}

.notes-section {
    background-color: #f9f7f1;
    border: 1px solid #8b4513;
    padding: 20px;
}

.notes-header {
    font-size: 16pt;
    font-weight: bold;
    margin-bottom: 15px;
}

.notes-content p:first-letter {
    font-variant: small-caps;
}

.notes-content p {
    text-indent: 1.5em;
    margin-bottom: 1em;
}

.cover-page {
    text-align: center;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
}

.cover-title {
    font-size: 36pt;
    font-weight: bold;
    margin-bottom: 20px;
}

.cover-subtitle {
    font-size: 24pt;
    margin-bottom: 40px;
}

.cover-image {
    margin: 40px auto;
    width: 300px;
    height: 200px;
}

.cover-date {
    font-size: 18pt;
    margin: 40px 0;
}

.cover-publisher {
    font-size: 14pt;
    position: absolute;
    bottom: 100px;
    width: 100%;
}

.toc-title {
    font-size: 24pt;
    font-weight: bold;
    text-align: center;
    margin: 40px 0;
}

.toc-entry {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    border-bottom: 1px dotted #d4c7a5;
}

.toc-lesson-number {
    width: 30px;
}

.toc-lesson-title {
    flex: 1;
    padding-left: 10px;
}

.toc-page-number {
    width: 30px;
    text-align: right;
}

.clearfix {
    clear: both;
}
"""

class LessonData:
    """Class to represent a single lesson and its components"""
    
    def __init__(self, number, title="", date=""):
        self.number = number
        self.title = title.strip().upper() if title else f"LESSON {number}"
        self.date = date
        self.questions = []
        self.notes = ""
    
    def add_question(self, text, scripture="", answer=""):
        """Add a question to the lesson"""
        self.questions.append({
            'text': text.strip(),
            'scripture': scripture.strip(),
            'answer': answer.strip()
        })
    
    def set_notes(self, notes):
        """Set the notes content"""
        self.notes = notes.strip()
    
    def __str__(self):
        return f"Lesson {self.number}: {self.title}, Questions: {len(self.questions)}, Notes: {'Yes' if self.notes else 'No'}"


class SabbathSchoolConverter:
    """Main class for converting Sabbath School lesson markdown to PDF"""
    
    def __init__(self):
        """Initialize the converter"""
        self.lessons = []
    
    def _preprocess_markdown(self, content):
        """Preprocess markdown to standardize formatting"""
        # Standardize headings for Questions and Notes sections
        content = re.sub(r'(?i)## questions', '### Questions', content)
        content = re.sub(r'(?i)## notes', '## Notes', content)
        
        # Standardize Lesson headings
        content = re.sub(r'(?i)# lesson (\d+)', r'# Lesson \1', content)
        
        return content
    
    def _extract_scripture_reference(self, text):
        """Extract scripture reference from question text"""
        scripture_match = re.search(r'([A-Za-z]+\. \d+:\d+(?:-\d+)?|\bVerses? \d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)', text)
        if scripture_match:
            return scripture_match.group(0)
        return ""
    
    def _extract_answer(self, text):
        """Extract answer from question text"""
        ans_match = re.search(r'(?:Ans\.|Answer:)(.*?)(?=\d+\.|$)', text, re.DOTALL)
        if ans_match:
            return ans_match.group(1).strip()
        return ""
    
    def _extract_questions(self, soup):
        """Extract questions from HTML soup"""
        questions = []
        
        # Try multiple strategies to find questions
        
        # Strategy 1: Look for a Questions section and find list items after it
        questions_section = None
        for heading in soup.find_all(['h2', 'h3']):
            if 'QUESTIONS' in heading.get_text().upper():
                questions_section = heading
                break
        
        if questions_section:
            # Look for the ordered list after the questions heading
            current_el = questions_section.next_sibling
            while current_el:
                if current_el.name == 'ol':
                    # Found an ordered list, extract questions from it
                    for li in current_el.find_all('li'):
                        text = li.get_text().strip()
                        scripture = self._extract_scripture_reference(text)
                        if scripture:
                            text = text.replace(scripture, "").strip()
                        
                        answer = self._extract_answer(text)
                        if answer:
                            text = text.replace(f"Ans.{answer}", "").replace(f"Answer:{answer}", "").strip()
                        
                        questions.append({
                            'text': text,
                            'scripture': scripture,
                            'answer': answer
                        })
                    break
                
                # No list found yet, continue looking
                current_el = current_el.next_sibling
        
        # Strategy 2: If no questions found with Strategy 1, look for numerical list items
        if not questions:
            list_items = []
            
            # Try to find ordered list items
            for ol in soup.find_all('ol'):
                for li in ol.find_all('li'):
                    list_items.append(li)
            
            # If no ordered lists, look for paragraphs that start with numbers
            if not list_items:
                for p in soup.find_all('p'):
                    text = p.get_text().strip()
                    if re.match(r'^\d+\.', text):
                        list_items.append(p)
            
            # Extract question data from the list items
            for item in list_items:
                text = item.get_text().strip()
                # Remove leading number if it exists
                text = re.sub(r'^\d+\.\s*', '', text)
                
                scripture = self._extract_scripture_reference(text)
                if scripture:
                    text = text.replace(scripture, "").strip()
                
                answer = self._extract_answer(text)
                if answer:
                    text = text.replace(f"Ans.{answer}", "").replace(f"Answer:{answer}", "").strip()
                
                questions.append({
                    'text': text,
                    'scripture': scripture,
                    'answer': answer
                })
        
        return questions
    
    def _extract_notes(self, soup):
        """Extract notes from HTML soup"""
        notes_content = []
        
        # Look for Notes section
        notes_section = None
        for heading in soup.find_all(['h2', 'h3']):
            if 'NOTES' in heading.get_text().upper():
                notes_section = heading
                break
        
        if notes_section:
            # Get all paragraphs after the Notes heading until the next heading
            current_el = notes_section.next_sibling
            while current_el:
                if current_el.name in ['h1', 'h2', 'h3']:
                    break
                    
                if current_el.name == 'p':
                    notes_content.append(current_el.get_text().strip())
                
                current_el = current_el.next_sibling
        
        # If no notes section found, try to find numerical notes
        if not notes_content:
            # Look for paragraphs starting with "Note X" or "X."
            note_paragraphs = []
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                if text.startswith('Note') or re.match(r'^\d+\.', text):
                    note_paragraphs.append(text)
            
            if note_paragraphs:
                notes_content = note_paragraphs
        
        return '\n\n'.join(notes_content)
    
    def _parse_sections_from_combined_file(self, content):
        """Parse individual lesson sections from a combined markdown file"""
        lessons = []
        
        # Try to find file sections marked with '# File: week-XX.md'
        file_sections = re.split(r'#\s+File:\s+([^\n]+)', content)
        
        if len(file_sections) > 1:
            logger.info(f"Found {(len(file_sections)-1)//2} file sections")
            
            # Process each section (odd indices are filenames, even indices are content)
            for i in range(1, len(file_sections), 2):
                if i+1 < len(file_sections):
                    filename = file_sections[i].strip()
                    section_content = file_sections[i+1].strip()
                    
                    # Check if it's a lesson/week file
                    lesson_match = re.search(r'(?i)week-(\d+)\.md', filename)
                    if lesson_match:
                        lesson_number = lesson_match.group(1)
                        
                        # Convert to HTML for parsing
                        section_html = markdown.markdown(section_content)
                        section_soup = BeautifulSoup(section_html, 'html.parser')
                        
                        # Extract lesson title from the first heading
                        title = ""
                        for heading in section_soup.find_all(['h1', 'h2']):
                            heading_text = heading.get_text().strip()
                            if 'LESSON' in heading_text.upper():
                                # Remove "Lesson X" prefix
                                title = re.sub(r'(?i)lesson\s+\d+\s*[-:]?\s*', '', heading_text).strip()
                            else:
                                title = heading_text
                            if title:
                                break
                        
                        # Get date if present
                        date_match = re.search(r'([A-Za-z]+ \d+, \d{4})', section_content)
                        lesson_date = date_match.group(1) if date_match else ""
                        
                        # Create a new lesson
                        lesson = LessonData(lesson_number, title, lesson_date)
                        
                        # Extract questions and notes
                        questions = self._extract_questions(section_soup)
                        for q in questions:
                            lesson.add_question(q['text'], q['scripture'], q['answer'])
                        
                        notes = self._extract_notes(section_soup)
                        lesson.set_notes(notes)
                        
                        lessons.append(lesson)
        
        return lessons
    
    def _parse_lessons_from_markdown(self, content):
        """Parse lessons from markdown content"""
        lessons = []
        
        # Preprocess markdown to standardize formatting
        content = self._preprocess_markdown(content)
        
        # Convert to HTML for parsing
        html_content = markdown.markdown(content)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all lesson headings
        lesson_headings = []
        for heading in soup.find_all(['h1', 'h2']):
            heading_text = heading.get_text().strip()
            if re.search(r'(?i)lesson\s+\d+', heading_text):
                lesson_headings.append(heading)
        
        if lesson_headings:
            logger.info(f"Found {len(lesson_headings)} lesson headings")
            
            # Process each lesson
            for i, heading in enumerate(lesson_headings):
                heading_text = heading.get_text().strip()
                
                # Extract lesson number
                lesson_match = re.search(r'(?i)lesson\s+(\d+)', heading_text)
                lesson_number = lesson_match.group(1) if lesson_match else str(i+1)
                
                # Extract date if present
                date_match = re.search(r'([A-Za-z]+ \d+, \d{4})', heading_text)
                lesson_date = date_match.group(1) if date_match else ""
                
                # Extract title (anything after lesson number and date)
                title_text = heading_text
                title_text = re.sub(r'(?i)lesson\s+\d+\s*[-:]?\s*', '', title_text)
                if date_match:
                    title_text = title_text.replace(date_match.group(1), '')
                title_text = title_text.strip(' -:')
                
                # Create a new lesson
                lesson = LessonData(lesson_number, title_text, lesson_date)
                
                # Find content until next lesson heading or end of document
                lesson_content = BeautifulSoup('', 'html.parser')
                current_el = heading.next_sibling
                
                # Find the next lesson heading if any
                next_heading = None
                if i < len(lesson_headings) - 1:
                    next_heading = lesson_headings[i+1]
                
                # Extract all content between current heading and next heading
                while current_el and current_el != next_heading:
                    if hasattr(current_el, 'name') and current_el.name:
                        # Create a copy of the node
                        lesson_content_html = str(lesson_content)
                        lesson_content = BeautifulSoup(f"{lesson_content_html}{str(current_el)}", 'html.parser')
                    current_el = current_el.next_sibling
                
                # Extract questions and notes
                questions = self._extract_questions(lesson_content)
                for q in questions:
                    lesson.add_question(q['text'], q['scripture'], q['answer'])
                
                notes = self._extract_notes(lesson_content)
                lesson.set_notes(notes)
                
                lessons.append(lesson)
        
        return lessons
    
    def parse_markdown_file(self, filepath):
        """Parse a markdown file and extract lessons"""
        try:
            # Read the file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Successfully read file: {filepath}")
            
            # Try first to parse as a standard file with lesson headings
            lessons = self._parse_lessons_from_markdown(content)
            
            # If no lessons found, try parsing as a combined file
            if not lessons:
                logger.info("No lessons found with standard parsing, trying combined file parsing")
                lessons = self._parse_sections_from_combined_file(content)
            
            # If still no lessons, create one lesson from the entire content
            if not lessons:
                logger.info("No lessons found with any parsing method, creating a single lesson")
                html_content = markdown.markdown(content)
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find a title
                title = "LESSON"
                for heading in soup.find_all(['h1', 'h2']):
                    title = heading.get_text().strip()
                    break
                
                lesson = LessonData("1", title)
                
                # Extract questions and notes
                questions = self._extract_questions(soup)
                for q in questions:
                    lesson.add_question(q['text'], q['scripture'], q['answer'])
                
                notes = self._extract_notes(soup)
                lesson.set_notes(notes)
                
                lessons.append(lesson)
            
            self.lessons = lessons
            
            # Log what we found
            logger.info(f"Found {len(self.lessons)} lessons")
            for lesson in self.lessons:
                logger.info(f"{lesson}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error parsing markdown file: {e}", exc_info=True)
            return False
    
    def _create_cover_page(self):
        """Create HTML for the cover page"""
        return """
        <div class="cover-page">
            <div class="cover-title">OLD TESTAMENT HISTORY</div>
            <div class="cover-subtitle">SABBATH-SCHOOL LESSONS<br>FOR SENIOR CLASSES</div>
            
            <div class="cover-image">
                <!-- Mountain and tablet illustration would go here -->
                <!-- Using a placeholder for now -->
                <div style="height: 200px; width: 300px; margin: 0 auto; position: relative;">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 70%; background-color: #a99d85; border-radius: 50% 50% 10% 10%;"></div>
                    <div style="position: absolute; bottom: 0; left: 25%; width: 50%; height: 50%; background-color: #e0d5c0; border: 2px solid #8b4513; border-radius: 5px;"></div>
                </div>
            </div>
            
            <div class="cover-date">
                <div style="font-style: italic; font-size: 14pt;">Originally Published</div>
                JANUARY TO JULY, 1889<br>
                <div style="font-style: italic; font-size: 14pt; margin-top: 10px;">by the</div>
                INTERNATIONAL SABBATH-SCHOOL ASSOCIATION
            </div>
            
            <div style="background-color: #f5f1e6; border: 1px solid #8b4513; border-radius: 10px; padding: 15px; width: 60%; margin: 0 auto;">
                <div style="font-weight: bold; font-size: 16pt;">REPRODUCED FOR</div>
                <div style="font-weight: bold; font-size: 16pt; margin-top: 5px;">QUARTER 1, 2025</div>
                <div style="font-size: 12pt; margin-top: 5px;">(January - March 2025)</div>
            </div>
            
            <div class="cover-publisher">
                <div style="font-weight: bold; font-size: 16pt;">GOSPEL SOUNDER</div>
                <div style="font-size: 12pt; margin-top: 5px;">Preserving the Truth for a New Generation</div>
            </div>
        </div>
        <div style="page-break-after: always;"></div>
        """
    
    def _create_table_of_contents(self):
        """Create HTML for the table of contents"""
        html = """
        <div class="toc-title">TABLE OF CONTENTS</div>
        <table class="toc-table" style="width: 100%; border-collapse: collapse;">
            <tr style="font-weight: bold; border-bottom: 2px solid #8b4513; margin-bottom: 10px;">
                <td style="width: 40px; padding: 5px;">Lesson</td>
                <td style="padding: 5px;">Title</td>
                <td style="width: 100px; padding: 5px;">Date</td>
                <td style="width: 40px; padding: 5px; text-align: right;">Page</td>
            </tr>
        """
        
        # Start page count from 1 (after cover and TOC)
        page_number = 3
        
        for lesson in self.lessons:
            html += f"""
            <tr style="border-bottom: 1px dotted #d4c7a5;">
                <td style="padding: 5px;">{lesson.number}</td>
                <td style="padding: 5px;">{lesson.title}</td>
                <td style="padding: 5px;">{lesson.date}</td>
                <td style="padding: 5px; text-align: right;">{page_number}</td>
            </tr>
            """
            page_number += 1  # Simple page count, one page per lesson
        
        html += """
        </table>
        <div style="page-break-after: always;"></div>
        """
        
        return html
    
    def _create_lesson_html(self, lesson):
        """Create HTML for a single lesson"""
        html = f"""
        <div class="lesson">
            <div class="lesson-header">
                <div class="corner top-left"></div>
                <div class="corner top-right"></div>
                <div class="corner bottom-left"></div>
                <div class="corner bottom-right"></div>
                <div class="lesson-circle">{lesson.number}</div>
                <div class="lesson-title">{lesson.title}</div>
                <div class="lesson-date">{lesson.date}</div>
            </div>
            
            <div class="questions-section">
                <div class="questions-header">QUESTIONS</div>
        """
        
        for i, question in enumerate(lesson.questions, 1):
            scripture = f'<span class="scripture-ref">{question["scripture"]}</span>' if question['scripture'] else ''
            answer = f'<div class="answer"><em>Ans. — {question["answer"]}</em></div>' if question['answer'] else ''
            
            html += f"""
            <div class="question">
                <span class="question-number">{i}.</span>
                <div class="question-text">
                    {question['text']} {scripture}
                    {answer}
                </div>
                <div class="clearfix"></div>
            </div>
            """
        
        html += """
            </div>
        """
        
        if lesson.notes:
            html += """
            <div class="notes-section">
                <div class="notes-header">NOTES</div>
                <div class="notes-content">
                    {0}
                </div>
            </div>
            """.format("".join('<p>{0}</p>'.format(para) for para in lesson.notes.split('\n\n') if para.strip()))
        
        html += """
        </div>
        <div style="page-break-after: always;"></div>
        """
        
        return html
    
    def generate_pdf(self, output_path):
        """Generate a PDF from the parsed lessons"""
        if not self.lessons:
            logger.error("No lessons to convert to PDF")
            return False
        
        try:
            # Create HTML for the complete document
            complete_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Old Testament History - Sabbath School Lessons</title>
                <style>
                {CSS_TEMPLATE}
                </style>
            </head>
            <body>
            """
            
            # Add cover page
            complete_html += self._create_cover_page()
            
            # Add table of contents
            complete_html += self._create_table_of_contents()
            
            # Add each lesson
            for lesson in self.lessons:
                complete_html += self._create_lesson_html(lesson)
            
            complete_html += """
            </body>
            </html>
            """
            
            # Create the PDF
            HTML(string=complete_html).write_pdf(output_path)
            
            logger.info(f"PDF created successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}", exc_info=True)
            return False


def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(
        description='Convert Sabbath School lesson markdown to PDF'
    )
    parser.add_argument('input_file', help='Input markdown file')
    parser.add_argument('output_file', help='Output PDF file')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate input file exists
    if not os.path.exists(args.input_file):
        logger.error(f"Input file does not exist: {args.input_file}")
        sys.exit(1)
    
    # Create converter and process file
    converter = SabbathSchoolConverter()
    
    if converter.parse_markdown_file(args.input_file):
        if converter.generate_pdf(args.output_file):
            logger.info("Conversion completed successfully!")
            sys.exit(0)
        else:
            logger.error("Failed to generate PDF")
            sys.exit(1)
    else:
        logger.error("Failed to parse markdown file")
        sys.exit(1)


if __name__ == "__main__":
    main()