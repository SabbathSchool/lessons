#!/usr/bin/env python3
"""
Sabbath School Lesson Markdown to PDF Converter

This script converts markdown files containing Sabbath School lessons
into beautifully formatted PDFs with a consistent design.

Requirements:
- Python 3.6+
- pip install markdown weasyprint python-frontmatter beautifulsoup4

Usage:
python3 markdown_to_pdf.py input_markdown.md output.pdf
"""

import os
import re
import sys
import argparse
import markdown
import frontmatter
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS
from datetime import datetime

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
        content: "Gospel Sounders - Q2 2025";
        font-family: Georgia, serif;
        font-size: 10pt;
        color: #5a4130;
    }
    @bottom-right {
        content: "Topical Studies on the Message";
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

.preliminary-note {
    font-style: italic;
    margin-bottom: 20px;
    padding: 10px 20px;
    background-color: #f9f7f1;
    border-left: 3px solid #8b4513;
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
    color: #3c1815;
}

.cover-subtitle {
    font-size: 24pt;
    margin-bottom: 40px;
    color: #5a4130;
}

.cover-image {
    margin: 40px auto;
    width: 300px;
    height: 200px;
}

.cover-date {
    font-size: 18pt;
    margin: 40px 0;
    color: #5a4130;
}

.cover-publisher {
    font-size: 14pt;
    position: absolute;
    bottom: 100px;
    width: 100%;
    color: #3c1815;
}

.toc-title {
    font-size: 24pt;
    font-weight: bold;
    text-align: center;
    margin: 40px 0;
    color: #3c1815;
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

def extract_questions(soup):
    """
    Extracts the questions from the HTML content
    """
    questions = []
    # Find all the list items that contain questions
    list_items = soup.find_all('li')
    
    for li in list_items:
        question_text = li.get_text().strip()
        
        # Extract scripture reference if it exists
        scripture_match = re.search(r'([A-Za-z]+\. \d+:\d+(?:-\d+)?|\bVerses? \d+(?:-\d+)?(?:, \d+(?:-\d+)?)*)', question_text)
        scripture_ref = scripture_match.group(0) if scripture_match else ""
        
        # Remove scripture reference from question text if it exists
        if scripture_match:
            question_text = question_text.replace(scripture_match.group(0), "").strip()
        
        # Extract answer if present
        ans_match = re.search(r'Ans\.(.*?)(?=\d+\.|$)', question_text, re.DOTALL)
        answer = ans_match.group(1).strip() if ans_match else ""
        
        # Remove answer from question text if it exists
        if ans_match:
            question_text = question_text.replace(ans_match.group(0), "").strip()
        
        questions.append({
            'text': question_text,
            'scripture': scripture_ref,
            'answer': answer
        })
    
    return questions

def generate_html(markdown_file):
    """
    Generates HTML content from the markdown file
    """
    # Read the markdown file
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse frontmatter if present
    try:
        post = frontmatter.loads(content)
        markdown_content = post.content
        metadata = post.metadata
    except:
        markdown_content = content
        metadata = {}
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract lessons
    lessons = []
    current_lesson = None
    
    for heading in soup.find_all(['h1']):  # Using h1 for lesson titles
        if "LESSON" in heading.get_text().upper():  # Case-insensitive match
            # Save previous lesson if exists
            if current_lesson:
                lessons.append(current_lesson)
            
            # Parse lesson header
            header_text = heading.get_text()
            lesson_match = re.search(r'LESSON (\d+)', header_text, re.IGNORECASE)
            title_match = re.search(r'- ([^\n]+)', header_text)
            
            lesson_number = lesson_match.group(1) if lesson_match else ""
            lesson_title = title_match.group(1).strip() if title_match else ""
            
            # Start new lesson
            current_lesson = {
                'number': lesson_number,
                'date': "",  # Will extract date separately
                'title': lesson_title,
                'preliminary_note': "",  # Added to store text before Questions
                'questions': [],
                'notes': ''
            }
            
            # Extract content following the heading
            current_element = heading.next_sibling
            
            # Look for the date (usually the next paragraph after the heading)
            while current_element and (not current_element.name or current_element.name != 'h2'):
                if current_element.name == 'p':
                    # Check if this looks like a date
                    date_text = current_element.get_text().strip()
                    date_match = re.search(r'([A-Za-z]+ \d+, \d{4})', date_text)
                    if date_match:
                        current_lesson['date'] = date_match.group(1)
                        current_element = current_element.next_sibling
                        break
                current_element = current_element.next_sibling
            
            # Extract any preliminary notes before Questions section
            preliminary_note = []
            while current_element and (not current_element.name or 'QUESTIONS' not in current_element.get_text().upper()):
                if current_element.name == 'p':
                    preliminary_note.append(current_element.get_text().strip())
                current_element = current_element.next_sibling
            
            if preliminary_note:
                current_lesson['preliminary_note'] = '\n\n'.join(preliminary_note)
            
            # Now get the Questions section
            if current_element and 'QUESTIONS' in current_element.get_text().upper():
                # Find content until Notes section or next lesson
                questions_content = BeautifulSoup('', 'html.parser')
                current_element = current_element.next_sibling
                
                while current_element and (not current_element.name or 'NOTES' not in current_element.get_text().upper() and not (current_element.name == 'h1' and 'LESSON' in current_element.get_text())):
                    if current_element.name:
                        questions_content.append(current_element)
                    current_element = current_element.next_sibling
                
                # Extract questions
                current_lesson['questions'] = extract_questions(questions_content)
                
                # Now get the Notes section if it exists
                if current_element and 'NOTES' in current_element.get_text().upper():
                    notes_content = []
                    current_element = current_element.next_sibling
                    
                    while current_element and (not current_element.name or not (current_element.name == 'h1' and 'LESSON' in current_element.get_text())):
                        if current_element.name == 'p':
                            notes_content.append(current_element.get_text().strip())
                        current_element = current_element.next_sibling
                    
                    if notes_content:
                        current_lesson['notes'] = '\n\n'.join(notes_content)
    
    # Add the last lesson
    if current_lesson:
        lessons.append(current_lesson)
    
    return lessons, metadata

def create_lesson_html(lesson):
    """
    Creates HTML for a single lesson
    """
    html = f"""
    <div class="lesson">
        <div class="lesson-header">
            <div class="corner top-left"></div>
            <div class="corner top-right"></div>
            <div class="corner bottom-left"></div>
            <div class="corner bottom-right"></div>
            <div class="lesson-circle">{lesson['number']}</div>
            <div class="lesson-title">{lesson['title']}</div>
            <div class="lesson-date">{lesson['date']}</div>
        </div>
    """
    
    # Add preliminary note if present
    # if lesson['preliminary_note']:
    #     html += f"""
    #     <div class="preliminary-note">
    #         <p>{lesson['preliminary_note'].replace('\n\n', '</p><p>')}</p>
    #     </div>
    #     """
    if lesson['preliminary_note']:
        html += """
        <div class="preliminary-note">
            <p>{preliminary_note}</p>
        </div>
        """.format(
            preliminary_note=lesson['preliminary_note'].replace('\n\n', '</p><p>')
        )

   

    
    html += """
        <div class="questions-section">
            <div class="questions-header">QUESTIONS</div>
    """
    
    for i, question in enumerate(lesson['questions'], 1):
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
    
    if lesson['notes']:
        html += """
        <div class="notes-section">
            <div class="notes-header">NOTES</div>
            <div class="notes-content">
                {notes_content}
            </div>
        </div>
        """.format(
            notes_content=''.join(
                '<p>{}</p>'.format(para) for para in lesson['notes'].split('\n\n') if para.strip()
            )
        )
    
    html += """
    </div>
    <div style="page-break-after: always;"></div>
    """
    
    return html

def create_cover_page():
    """
    Creates the cover page HTML using the SVG design
    """
    # The SVG is embedded directly - you can replace with the specific design you choose
    svg_content = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="800" height="1000">
      <!-- Full page background for printing -->
      <rect width="800" height="1000" fill="#ffffff"/>
      
      <!-- Decorative border -->
      <rect x="30" y="30" width="740" height="940" stroke="#7d2b2b" stroke-width="3" fill="none"/>
      <rect x="40" y="40" width="720" height="920" stroke="#7d2b2b" stroke-width="1" fill="none"/>
      
      <!-- Corner ornaments -->
      <path d="M30,30 L80,30 L80,45 Q55,45 55,70 L40,70 L40,55 Q40,30 30,30 Z" fill="#7d2b2b"/>
      <path d="M770,30 L720,30 L720,45 Q745,45 745,70 L760,70 L760,55 Q760,30 770,30 Z" fill="#7d2b2b"/>
      <path d="M30,970 L80,970 L80,955 Q55,955 55,930 L40,930 L40,945 Q40,970 30,970 Z" fill="#7d2b2b"/>
      <path d="M770,970 L720,970 L720,955 Q745,955 745,930 L760,930 L760,945 Q760,970 770,970 Z" fill="#7d2b2b"/>
      
      <!-- Main title with burgundy and gold color scheme -->
      <text x="400" y="170" font-family="Georgia, serif" font-size="48" font-weight="bold" text-anchor="middle" fill="#7d2b2b">TOPICAL STUDIES</text>
      <text x="400" y="230" font-family="Georgia, serif" font-size="48" font-weight="bold" text-anchor="middle" fill="#7d2b2b">ON THE MESSAGE</text>
      
      <!-- Subtitle -->
      <text x="400" y="310" font-family="Georgia, serif" font-size="28" text-anchor="middle" fill="#c9a227">SABBATH-SCHOOL LESSONS</text>
      <text x="400" y="350" font-family="Georgia, serif" font-size="28" text-anchor="middle" fill="#c9a227">FOR SENIOR CLASSES</text>
      
      <!-- Sanctuary Ark of Covenant illustration with glow -->
      <defs>
        <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#e6ca7c"/>
          <stop offset="50%" stop-color="#c9a227"/>
          <stop offset="100%" stop-color="#e6ca7c"/>
        </linearGradient>
        <radialGradient id="arkGlow" cx="50%" cy="50%" r="60%" fx="50%" fy="50%">
          <stop offset="0%" stop-color="#fcf6e6" stop-opacity="0.8"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
        </radialGradient>
      </defs>
      
      <!-- Glow behind ark -->
      <circle cx="400" cy="500" r="150" fill="url(#arkGlow)"/>
      
      <!-- Ark base -->
      <rect x="300" y="490" width="200" height="110" fill="url(#goldGradient)" stroke="#7d2b2b" stroke-width="2"/>
      
      <!-- Ark lid/mercy seat -->
      <rect x="290" y="480" width="220" height="20" rx="5" ry="5" fill="url(#goldGradient)" stroke="#7d2b2b" stroke-width="2"/>
      
      <!-- Cherubs (simplified) -->
      <path d="M320,480 C310,460 320,440 330,430 C340,440 340,470 335,480" fill="url(#goldGradient)" stroke="#7d2b2b" stroke-width="1.5"/>
      <path d="M480,480 C490,460 480,440 470,430 C460,440 460,470 465,480" fill="url(#goldGradient)" stroke="#7d2b2b" stroke-width="1.5"/>
      
      <!-- Cherub wings -->
      <path d="M335,465 C350,455 370,455 380,460" fill="none" stroke="#7d2b2b" stroke-width="1.5"/>
      <path d="M465,465 C450,455 430,455 420,460" fill="none" stroke="#7d2b2b" stroke-width="1.5"/>
      
      <!-- Decorative elements on the ark -->
      <rect x="320" y="510" width="160" height="70" fill="none" stroke="#7d2b2b" stroke-width="1"/>
      
      <!-- Tables of stone inside ark -->
      <rect x="350" y="500" width="40" height="50" rx="3" ry="3" fill="#f5f1e6" stroke="#7d2b2b" stroke-width="0.5"/>
      <rect x="410" y="500" width="40" height="50" rx="3" ry="3" fill="#f5f1e6" stroke="#7d2b2b" stroke-width="0.5"/>
      
      <!-- Text lines on the tables of stone -->
      <line x1="355" y1="510" x2="385" y2="510" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="355" y1="515" x2="385" y2="515" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="355" y1="520" x2="385" y2="520" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="355" y1="525" x2="385" y2="525" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="355" y1="530" x2="385" y2="530" stroke="#7d2b2b" stroke-width="0.5"/>
      
      <line x1="415" y1="510" x2="445" y2="510" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="415" y1="515" x2="445" y2="515" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="415" y1="520" x2="445" y2="520" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="415" y1="525" x2="445" y2="525" stroke="#7d2b2b" stroke-width="0.5"/>
      <line x1="415" y1="530" x2="445" y2="530" stroke="#7d2b2b" stroke-width="0.5"/>
      
      <!-- Light rays from the mercy seat -->
      <path d="M400,430 L400,350" stroke="#fcf6e6" stroke-width="15" opacity="0.7"/>
      <path d="M380,440 L340,380" stroke="#fcf6e6" stroke-width="12" opacity="0.6"/>
      <path d="M420,440 L460,380" stroke="#fcf6e6" stroke-width="12" opacity="0.6"/>
      <path d="M360,450 L300,410" stroke="#fcf6e6" stroke-width="8" opacity="0.5"/>
      <path d="M440,450 L500,410" stroke="#fcf6e6" stroke-width="8" opacity="0.5"/>
      
      <!-- Original Publication Info -->
      <text x="400" y="670" font-family="Georgia, serif" font-size="16" font-style="italic" text-anchor="middle" fill="#7d2b2b">Originally Published by the</text>
      <text x="400" y="695" font-family="Georgia, serif" font-size="18" text-anchor="middle" fill="#7d2b2b">PACIFIC PRESS PUBLISHING CO., 1905</text>
      <text x="400" y="720" font-family="Georgia, serif" font-size="16" text-anchor="middle" fill="#7d2b2b">REPRODUCED BY GOSPEL SOUNDERS MINISTRY</text>
      
      <!-- Quarter info -->
      <rect x="150" y="780" width="500" height="90" rx="10" ry="10" fill="#f7f1e3" stroke="#c9a227" stroke-width="1"/>
      <text x="400" y="810" font-family="Georgia, serif" font-size="22" font-weight="bold" text-anchor="middle" fill="#7d2b2b">SECOND QUARTER, 2025</text>
      <text x="400" y="840" font-family="Georgia, serif" font-size="18" text-anchor="middle" fill="#7d2b2b">April - June 2025</text>
      
      <!-- Publisher Footer -->
      <text x="400" y="920" font-family="Georgia, serif" font-size="18" font-weight="bold" text-anchor="middle" fill="#7d2b2b">GOSPEL SOUNDERS</text>
      <text x="400" y="945" font-family="Georgia, serif" font-size="14" text-anchor="middle" fill="#7d2b2b">Preserving the Truth for a New Generation</text>
    </svg>
    """
    
    return f"""
    <div class="cover-page">
        {svg_content}
    </div>
    <div style="page-break-after: always;"></div>
    """

def create_table_of_contents(lessons):
    """
    Creates the table of contents HTML
    """
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
    
    for lesson in lessons:
        html += f"""
        <tr style="border-bottom: 1px dotted #d4c7a5;">
            <td style="padding: 5px;">{lesson['number']}</td>
            <td style="padding: 5px;">{lesson['title']}</td>
            <td style="padding: 5px;">{lesson['date']}</td>
            <td style="padding: 5px; text-align: right;">{page_number}</td>
        </tr>
        """
        page_number += 1  # Simple page count, one page per lesson
    
    html += """
    </table>
    <div style="page-break-after: always;"></div>
    """
    
    return html

def convert_markdown_to_pdf(markdown_file, output_pdf):
    """
    Converts a markdown file to PDF with the specified design
    """
    lessons, metadata = generate_html(markdown_file)
    
    # For debugging - uncomment to see what lessons were extracted
    # print(f"Found {len(lessons)} lessons:")
    # for lesson in lessons:
    #     print(f"Lesson {lesson['number']}: {lesson['title']} ({lesson['date']})")
    #     print(f"Questions: {len(lesson['questions'])}")
    #     print(f"Notes: {'Yes' if lesson['notes'] else 'No'}")
    #     print(f"Preliminary: {'Yes' if lesson['preliminary_note'] else 'No'}")
    #     print()
    
    # Create HTML for the complete document
    complete_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Topical Studies on the Message - Sabbath School Lessons</title>
        <style>
        {CSS_TEMPLATE}
        </style>
    </head>
    <body>
    """
    
    # Add cover page using the SVG design
    complete_html += create_cover_page()
    
    # Add table of contents
    complete_html += create_table_of_contents(lessons)
    
    # Add each lesson
    for lesson in lessons:
        complete_html += create_lesson_html(lesson)
    
    complete_html += """
    </body>
    </html>
    """
    
    # For debugging - uncomment to save the generated HTML
    debug_html_path = output_pdf.replace('.pdf', '_debug.html')
    with open(debug_html_path, 'w', encoding='utf-8') as f:
        f.write(complete_html)
    print(f"Debug HTML saved to: {debug_html_path}")
    
    # Create the PDF
    HTML(string=complete_html).write_pdf(output_pdf)
    
    print(f"PDF created successfully: {output_pdf}")

def main():
    parser = argparse.ArgumentParser(description='Convert Sabbath School lesson markdown to PDF')
    parser.add_argument('input_file', help='Input markdown file')
    parser.add_argument('output_file', help='Output PDF file')
    
    args = parser.parse_args()
    
    convert_markdown_to_pdf(args.input_file, args.output_file)

if __name__ == "__main__":
    main()