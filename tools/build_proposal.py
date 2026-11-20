"""Build the one-page English proposal from its Markdown source.

Layout verification is performed separately using a rendered page image.
"""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'deliverables/proposal.md'
OUTPUT = ROOT / 'deliverables/ECO6109_Project_Proposal.docx'


def font_settings(style, size, bold=False):
    style.font.name = 'Times New Roman'
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    fonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in ['ascii', 'hAnsi', 'eastAsia', 'cs']:
        fonts.set(qn('w:' + attr), 'Times New Roman')
    for attr in ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme']:
        fonts.attrib.pop(qn('w:' + attr), None)


def main():
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.54)
    section.left_margin = section.right_margin = Cm(3.18)
    normal = doc.styles['Normal']
    font_settings(normal, 12)
    normal.paragraph_format.line_spacing = 1.2
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.first_line_indent = Cm(.5)
    normal.paragraph_format.widow_control = True
    title = doc.styles['Title']
    font_settings(title, 14, True)
    title.paragraph_format.first_line_indent = Cm(0)
    title.paragraph_format.line_spacing = 1.05
    title.paragraph_format.space_before = Pt(0)
    title.paragraph_format.space_after = Pt(6)
    title.paragraph_format.keep_with_next = True
    heading = doc.styles['Heading 1']
    font_settings(heading, 12.5, True)
    heading.paragraph_format.first_line_indent = Cm(0)
    heading.paragraph_format.line_spacing = 1.0
    heading.paragraph_format.space_before = Pt(6)
    heading.paragraph_format.space_after = Pt(3)
    heading.paragraph_format.keep_with_next = True
    # Prevent Word themes from adding decorative title rules or paragraph fills.
    for style in [normal, title, heading]:
        ppr = style.element.find(qn('w:pPr'))
        if ppr is not None:
            for child in list(ppr):
                if child.tag in [qn('w:pBdr'), qn('w:shd')]:
                    ppr.remove(child)
    text = SOURCE.read_text(encoding='utf-8')
    chunks = text.strip().split('\n\n')
    for i, chunk in enumerate(chunks):
        if chunk.startswith('# '):
            p = doc.add_paragraph(chunk[2:], style='Title')
        elif chunk.startswith('## '):
            p = doc.add_paragraph(chunk[3:], style='Heading 1')
        else:
            p = doc.add_paragraph(chunk)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            if i == 1:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.space_after = Pt(7)
                p.paragraph_format.keep_with_next = True
    settings = doc.settings.element
    language = OxmlElement('w:themeFontLang')
    language.set(qn('w:val'), 'en-US')
    settings.append(language)
    doc.core_properties.title = chunks[0][2:]
    doc.core_properties.subject = 'ECO6109 Group Project Proposal'
    doc.core_properties.author = ''
    doc.core_properties.last_modified_by = ''
    doc.core_properties.comments = ''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    body_words = sum(len(c.split()) for c in chunks if not c.startswith('#'))
    print(f'Created {OUTPUT}')
    print(f'Body and metadata words: {body_words}')


if __name__ == '__main__':
    main()
