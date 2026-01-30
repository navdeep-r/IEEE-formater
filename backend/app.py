from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import tempfile
import subprocess
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

def generate_latex_document(form_data):
    """Generate LaTeX code for IEEE conference paper based on form data"""
    
    # Process title and funding
    title = form_data.get('title', 'Conference Paper Title*')
    funding = form_data.get('funding', '')
    paper_notice = form_data.get('paperNotice', '')
    drop_cap = form_data.get('dropCap', True)
    
    title_latex = f"{title}*\\\\\n{{\\footnotesize \\textsuperscript{{*}}Note: Sub-titles are not captured for https://ieeexplore.ieee.org and should not be used}}"
    
    if funding:
        title_latex += f"\n\\thanks{{{funding}}}"
    
    # Process authors
    authors = form_data.get('authors', [])
    author_blocks = []
    
    for i, author in enumerate(authors):
        # Format:
        # \IEEEauthorblockN{1\textsuperscript{st} Given Name Surname \IEEEmembership{Member, IEEE}}
        
        ordinal_suffix = "th"
        if (i + 1) % 10 == 1 and (i + 1) % 100 != 11:
            ordinal_suffix = "st"
        elif (i + 1) % 10 == 2 and (i + 1) % 100 != 12:
            ordinal_suffix = "nd"
        elif (i + 1) % 10 == 3 and (i + 1) % 100 != 13:
            ordinal_suffix = "rd"
            
        ordinal = f"{i + 1}\\textsuperscript{{{ordinal_suffix}}}"
        
        name = f"{ordinal} {author.get('firstName', '')} {author.get('lastName', '')}"
        membership = author.get('membership', '')
        if membership:
            name += f" \\IEEEmembership{{{membership}}}"
            
        dept = author.get('department', '')
        org = author.get('organization', '')
        loc = author.get('cityCountry', '')
        email = author.get('email', '')
        
        block = f"\\IEEEauthorblockN{{{name}}}\n"
        block += f"\\IEEEauthorblockA{{\\textit{{{dept}}} \\\\\n"
        block += f"\\textit{{{org}}}\\\\\n"
        block += f"{loc} \\\\\n"
        block += f"{email}}}"
        
        author_blocks.append(block)
        
    authors_str = '\n\\and\n'.join(author_blocks)
    
    # Process abstract
    abstract = form_data.get('abstract', '')
    
    # Process keywords
    keywords = form_data.get('keywords', '')
    
    # Process sections
    sections = form_data.get('sections', [])
    sections_latex = []
        
    for i, section in enumerate(sections):
        title_sec = section.get('title', 'Section')
        content_sec = section.get('content', '')
        
        # Handle Drop Cap for the first section if enabled
        if i == 0 and drop_cap and content_sec:
            # \IEEEPARstart{F}{irst} word...
            # We need to split the first word
            words = content_sec.split(' ', 1)
            if words:
                first_word = words[0]
                rest_of_text = words[1] if len(words) > 1 else ''
                
                if len(first_word) > 1:
                    first_letter = first_word[0]
                    rest_of_word = first_word[1:]
                    content_sec = f"\\IEEEPARstart{{{first_letter}}}{{{rest_of_word}}} {rest_of_text}"
                else:
                    # Single letter word? unusual but handle it
                    content_sec = f"\\IEEEPARstart{{{first_word}}}{{}} {rest_of_text}"
        
        sections_latex.append(f"\\section{{{title_sec}}}\n{content_sec}")
    
    # Join sections
    sections_content = '\n\n'.join(sections_latex)
    
    # Process references
    references = form_data.get('references', '')
    
    # Create the complete LaTeX document
    # Inject special paper notice if present
    special_notice_cmd = ""
    if paper_notice:
        special_notice_cmd = f"\\IEEEspecialpapernotice{{{paper_notice}}}\n"

    latex_template = f"""\\documentclass[conference]{{IEEEtran}}
\\IEEEoverridecommandlockouts
% The preceding line is only needed to identify funding in the first footnote. If that is unneeded, please comment it out.
%Template version as of 6/27/2024

\\usepackage{{cite}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{algorithmic}}
\\usepackage{{graphicx}}
\\usepackage{{textcomp}}
\\usepackage{{xcolor}}
\\def\\BibTeX{{{{\\rm B\\kern-.05em{{\\sc i\\kern-.025em b}}\\kern-.08em
    T\\kern-.1667em\\lower.7ex\\hbox{{E}}\\kern-.125emX}}}}
\\begin{{document}}

\\title{{{title_latex}}}

{special_notice_cmd}
\\author{{{authors_str}}}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\begin{{IEEEkeywords}}
{keywords}
\\end{{IEEEkeywords}}

{sections_content}

\\begin{{thebibliography}}{{00}}
{references}
\\end{{thebibliography}}

\\end{{document}}"""
    
    return latex_template

def to_roman(num):
    """Convert integer to Roman numeral"""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    for i in range(len(val)):
        count = int(num / val[i])
        roman_num += syb[i] * count
        num -= val[i] * count
    return roman_num

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        form_data = request.json
        
        # Extract variables from form data for use in both LaTeX and fallback
        # Extract variables from form data for use in both LaTeX and fallback
        title = form_data.get('title', 'Untitled Paper')
        funding = form_data.get('funding', '')
        paper_notice = form_data.get('paperNotice', '') # New field
        drop_cap = form_data.get('dropCap', True) # New field
        authors = form_data.get('authors', [])
        abstract = form_data.get('abstract', '')
        keywords = form_data.get('keywords', '')
        sections = form_data.get('sections', [])
        references = form_data.get('references', '')
                
        # Generate LaTeX code
        latex_code = generate_latex_document(form_data)
                
        # Create temporary directory and files
        temp_dir = tempfile.mkdtemp()
        try:
            tex_file_path = os.path.join(temp_dir, 'paper.tex')
                    
            # Write LaTeX code to file
            with open(tex_file_path, 'w', encoding='utf-8') as f:
                f.write(latex_code)
                    
            # Compile LaTeX to PDF using pdflatex
            try:
                result = subprocess.run([
                    'pdflatex', 
                    '-include-directory=' + temp_dir,
                    '-output-directory=' + temp_dir,
                    tex_file_path
                ], capture_output=True, text=True, timeout=30)
                        
                if result.returncode != 0:
                    print(f"LaTeX compilation failed: {result.stderr}")
                    raise Exception("LaTeX compilation failed")
                            
                pdf_file_path = os.path.join(temp_dir, 'paper.pdf')
                        
                # Check if PDF was created
                if not os.path.exists(pdf_file_path):
                    # Try alternative PDF names
                    alt_pdf_path = os.path.join(temp_dir, 'paper.PDF')
                    if os.path.exists(alt_pdf_path):
                        pdf_file_path = alt_pdf_path
                    else:
                        raise FileNotFoundError("PDF file was not created")
                                
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
                print(f"LaTeX compilation failed: {str(e)}. Using fallback method.")
                
                # High-quality fallback using ReportLab Platypus
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, Flowable
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
                from reportlab.lib import colors
                from reportlab.lib.units import inch, mm
                
                # Setup document
                buffer = io.BytesIO()
                doc = BaseDocTemplate(buffer, pagesize=A4,
                                    leftMargin=0.6*inch, rightMargin=0.6*inch,
                                    topMargin=0.7*inch, bottomMargin=0.7*inch)
                
                # Styles
                styles = getSampleStyleSheet()
                
                # Title Style
                title_style = ParagraphStyle(
                    'IEEE_Title',
                    parent=styles['Heading1'],
                    fontName='Times-Bold',
                    fontSize=24,
                    leading=28,
                    alignment=TA_CENTER,
                    spaceAfter=6,
                    textColor=colors.black
                )
                
                # Subtitle/Note Style
                subtitle_style = ParagraphStyle(
                    'IEEE_Subtitle',
                    parent=styles['Normal'],
                    fontName='Times-Roman',
                    fontSize=8,
                    leading=10,
                    alignment=TA_CENTER,
                    spaceAfter=12
                )
                
                 # Special Paper Notice Style
                notice_style = ParagraphStyle(
                    'IEEE_Notice',
                    parent=styles['Normal'],
                    fontName='Times-Italic',
                    fontSize=10,
                    leading=12,
                    alignment=TA_CENTER,
                    spaceAfter=12
                )

                # Author Style
                author_name_style = ParagraphStyle(
                    'IEEE_Author_Name',
                    parent=styles['Normal'],
                    fontName='Times-Roman',
                    fontSize=11,
                    leading=13,
                    alignment=TA_CENTER
                )
                
                author_affil_style = ParagraphStyle(
                    'IEEE_Author_Affil',
                    parent=styles['Normal'],
                    fontName='Times-Italic',
                    fontSize=10,
                    leading=12,
                    alignment=TA_CENTER
                )
                
                # Body Text Style (Times-Roman, Justified)
                body_style = ParagraphStyle(
                    'IEEE_Body',
                    parent=styles['Normal'],
                    fontName='Times-Roman',
                    fontSize=10,
                    leading=12,
                    alignment=TA_JUSTIFY
                )
                
                # Drop Cap First Letter Style
                drop_cap_style = ParagraphStyle(
                    'IEEE_DropCap',
                    parent=body_style,
                    fontSize=24,
                    leading=24,
                    fontName='Times-Bold'
                )

                # Heading sections
                h1_style = ParagraphStyle(
                    'IEEE_H1',
                    parent=styles['Heading2'],
                    fontName='Times-Roman', # IEEE uses Small Caps often but Roman is fine
                    fontSize=10,
                    leading=12,
                    alignment=TA_CENTER,
                    spaceBefore=12,
                    spaceAfter=6,
                    textTransform='uppercase' 
                )
                
                # --- Page Layout Definitions ---
                page_width, page_height = A4
                left_margin = 0.6*inch
                right_margin = 0.6*inch
                top_margin = 0.7*inch
                bottom_margin = 0.7*inch
                
                # --- MEASURE HEADER HEIGHT DYNAMICALLY ---
                # We need to know how tall the title, notices, authors, abstract, and keywords are
                # so we can size the 'Header Frame' correctly and push the columns down.

                available_width = page_width - left_margin - right_margin
                
                # We will collect the flowables for the header here first to measure them
                header_story = []
                
                # 1. Title
                t_para = Paragraph(title + "*", title_style)
                header_story.append(t_para)
                header_story.append(Paragraph("<i>*Note: Sub-titles are not captured for https://ieeexplore.ieee.org and should not be used</i>", subtitle_style))
                
                if paper_notice:
                    header_story.append(Paragraph(paper_notice, notice_style))

                if funding:
                    header_story.append(Paragraph(f"<i>Funding: {funding}</i>", subtitle_style))
                
                header_story.append(Spacer(1, 10))
                
                # 2. Authors (Grid Layout)
                # Group authors into rows of 3
                author_rows = []
                current_row = []
                for i, author in enumerate(authors):
                    # Format author text
                    ordinal_suffix = "th"
                    val = i + 1
                    if val % 10 == 1 and val % 100 != 11: ordinal_suffix = "st"
                    elif val % 10 == 2 and val % 100 != 12: ordinal_suffix = "nd"
                    elif val % 10 == 3 and val % 100 != 13: ordinal_suffix = "rd"
                    
                    membership_txt = ""
                    if author.get('membership'):
                        membership_txt = f" <i>{author.get('membership')}</i>"

                    name_text = f"{val}<sup>{ordinal_suffix}</sup> {author.get('firstName', '')} {author.get('lastName', '')}{membership_txt}"
                    affil_text = f"{author.get('department', '')}<br/>{author.get('organization', '')}<br/>{author.get('cityCountry', '')}<br/>{author.get('email', '')}"
                    
                    # Create cell content
                    cell_content = [
                        Paragraph(name_text, author_name_style),
                        Paragraph(affil_text, author_affil_style)
                    ]
                    current_row.append(cell_content)
                    
                    if len(current_row) == 3:
                        author_rows.append(current_row)
                        current_row = []
                
                if current_row:
                    # Pad the last row if needed
                    while len(current_row) < 3:
                        current_row.append("")
                    author_rows.append(current_row)
                
                # Create Table
                if author_rows:
                    table = Table(author_rows, colWidths=[available_width/3.0]*3)
                    table.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('LEFTPADDING', (0,0), (-1,-1), 2),
                        ('RIGHTPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    ]))
                    header_story.append(table)
                    header_story.append(Spacer(1, 10))
                
                # 3. Abstract
                if abstract:
                    abs_text = f"<b><i>Abstract</i></b>—{abstract.replace('Abstract—', '')}"
                    header_story.append(Paragraph(abs_text, ParagraphStyle('Abs', parent=body_style, fontName='Times-Bold', leftIndent=0, rightIndent=0)))
                    header_story.append(Spacer(1, 6))
                
                # 4. Keywords
                if keywords:
                    kw_text = f"<b><i>Index Terms</i></b>—{keywords.replace('Keywords—', '')}"
                    header_story.append(Paragraph(kw_text, ParagraphStyle('Kw', parent=body_style, fontName='Times-Bold')))
                    header_story.append(Spacer(1, 12))
                    
                # Calculate total height
                total_header_height = 0
                for elem in header_story:
                    w, h = elem.wrap(available_width, page_height)
                    total_header_height += h
                
                # Add a little buffer
                header_buffer = 0.2 * inch
                calculated_header_height = total_header_height + header_buffer
                
                # --- Construct Main Story ---
                story = list(header_story)
                
                # 5. Sections
                for i, section in enumerate(sections):
                    # Section Title
                    sec_num = to_roman(i + 1)
                    sec_title = f"{sec_num}. {section.get('title', 'Section').upper()}"
                    story.append(Paragraph(sec_title, h1_style))
                    
                    # Content
                    content_txt = section.get('content', '')
                    
                    # Simulated Drop Cap for first section only
                    # Note: We are already past the header, so this is in the columns now.
                    if i == 0 and drop_cap and content_txt:
                         # Simple simulation: Make first letter bigger and bold
                         if len(content_txt) > 0:
                            first_letter = content_txt[0]
                            rest = content_txt[1:].replace('\n', '<br/>')
                            content_clean = f'<font size="20"><b>{first_letter}</b></font>{rest}'
                            story.append(Paragraph(content_clean, body_style))
                    else:
                        content_clean = content_txt.replace('\n', '<br/>')
                        story.append(Paragraph(content_clean, body_style))
                        
                    story.append(Spacer(1, 10))
                
                # 6. References
                if references:
                    story.append(Paragraph("REFERENCES", h1_style))
                    # Basic split
                    ref_list = references.split('\n')
                    for ref in ref_list:
                        if ref.strip():
                            story.append(Paragraph(ref, body_style))
                            story.append(Spacer(1, 4))
                
                # --- Page Templates ---
                # Define Frames
                # Layout: Top Header Area (for title/auth), then 2 Columns below
                
                full_width = page_width - left_margin - right_margin
                col_gap = 0.2*inch
                col_width = (full_width - col_gap) / 2
                
                # Frame 1: Header (Dynamic Height)
                header_frame = Frame(
                    left_margin, 
                    page_height - top_margin - calculated_header_height, 
                    full_width, 
                    calculated_header_height,
                    id='header',
                    showBoundary=0
                )
                
                # Columns for First Page (starts below header)
                # Height = (Top Y) - (Bottom Y)
                # Top Y = page_height - top_margin - calculated_header_height - 0.1*inch
                # Bottom Y = bottom_margin
                first_page_col_height = page_height - top_margin - calculated_header_height - 0.1*inch - bottom_margin
                
                col1_first = Frame(
                    left_margin, 
                    bottom_margin, 
                    col_width, 
                    first_page_col_height,
                    id='col1_first',
                    showBoundary=0
                )
                
                col2_first = Frame(
                    left_margin + col_width + col_gap, 
                    bottom_margin, 
                    col_width, 
                    first_page_col_height,
                    id='col2_first',
                    showBoundary=0
                )
                
                # Columns for Subsequent Pages (full height)
                col1_normal = Frame(
                    left_margin, 
                    bottom_margin, 
                    col_width, 
                    page_height - top_margin - bottom_margin,
                    id='col1_normal'
                )
                
                col2_normal = Frame(
                    left_margin + col_width + col_gap, 
                    bottom_margin, 
                    col_width, 
                    page_height - top_margin - bottom_margin,
                    id='col2_normal'
                )
                
                # Templates
                template_first = PageTemplate(
                    id='FirstPage', 
                    frames=[header_frame, col1_first, col2_first],
                    onPage=lambda canvas, doc: None # No special drawing
                )
                
                template_normal = PageTemplate(
                    id='NormalPage', 
                    frames=[col1_normal, col2_normal]
                )
                
                doc.addPageTemplates([template_first, template_normal])
                
                # Build
                doc.build(story)
                
                buffer.seek(0)
                
                # Save to temp file
                pdf_file_path = os.path.join(temp_dir, 'paper.pdf')
                with open(pdf_file_path, 'wb') as f:
                    f.write(buffer.getvalue())
            
            return send_file(pdf_file_path, as_attachment=True, download_name='ieee_conference_paper.pdf')
        finally:
            # Clean up temp directory after sending the file
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return jsonify({"message": "IEEE Paper Generator API is running!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)