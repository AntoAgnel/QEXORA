"""
Editor PDF Export Service
Renders the visual editor's block layout into a professional PDF.
Supports text blocks, question blocks, image blocks, dividers.
"""
from io import BytesIO
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.utils import ImageReader
from io import BytesIO as BIO
import re

ACCENT     = colors.HexColor('#6c63ff')
ACCENT2    = colors.HexColor('#00d4aa')
LIGHT_GRAY = colors.HexColor('#f4f4f8')
MID_GRAY   = colors.HexColor('#8a8fa8')
BLACK      = colors.black
WHITE      = colors.white

ALIGN_MAP = {
    'left':    TA_LEFT,
    'center':  TA_CENTER,
    'right':   TA_RIGHT,
    'justify': TA_JUSTIFY,
}


def _make_style(block: dict) -> ParagraphStyle:
    align_key = block.get('align', 'left')
    return ParagraphStyle(
        'blk',
        fontName  = 'Helvetica-Bold' if block.get('bold') else 'Helvetica',
        fontSize  = int(block.get('fontSize', 11)),
        textColor = _hex_to_color(block.get('color', '#1a1a2e')),
        alignment = ALIGN_MAP.get(align_key, TA_LEFT),
        leading   = int(block.get('fontSize', 11)) * 1.5,
        spaceAfter= 4,
    )


def _hex_to_color(hex_str: str):
    hex_str = hex_str.lstrip('#')
    try:
        r, g, b = int(hex_str[0:2],16), int(hex_str[2:4],16), int(hex_str[4:6],16)
        return colors.Color(r/255, g/255, b/255)
    except Exception:
        return BLACK


def _process_block(block: dict, story: list):
    btype = block.get('type', 'text')

    if btype == 'divider':
        color_val = _hex_to_color(block.get('color', '#6c63ff'))
        story.append(HRFlowable(
            width='100%',
            thickness=float(block.get('thickness', 1.5)),
            color=color_val,
            spaceAfter=8, spaceBefore=8
        ))

    elif btype == 'spacer':
        story.append(Spacer(1, float(block.get('height', 12))))

    elif btype == 'image':
        src = block.get('src', '')
        if src and src.startswith('data:image'):
            # Strip data URI header
            try:
                header, b64data = src.split(',', 1)
                img_bytes = base64.b64decode(b64data)
                img_buf   = BIO(img_bytes)
                w = float(block.get('width', 8)) * cm
                h = float(block.get('height', 5)) * cm
                img = Image(img_buf, width=w, height=h)
                align = block.get('align', 'center')
                img.hAlign = align.upper()
                story.append(img)
                story.append(Spacer(1, 6))
            except Exception as e:
                print(f"[EditorExport] Image error: {e}")

    elif btype in ('text', 'title', 'subtitle', 'heading',
                   'question', 'instruction', 'footer'):
        content = block.get('content', '').strip()
        if not content:
            story.append(Spacer(1, 6))
            return
        # Escape XML special chars
        content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Apply bold/italic via tags if set
        if block.get('bold') and block.get('italic'):
            content = f'<b><i>{content}</i></b>'
        elif block.get('bold'):
            content = f'<b>{content}</b>'
        elif block.get('italic'):
            content = f'<i>{content}</i>'

        style = _make_style(block)
        story.append(Paragraph(content, style))

    elif btype == 'question_list':
        questions = block.get('questions', [])
        marks_col = block.get('show_marks', True)
        mapping_col = block.get('show_mapping', True)

        if not questions:
            return

        section_name = block.get('section_name', '')
        mpq          = block.get('marks_per_question', 2)

        if section_name:
            heading_style = ParagraphStyle('sh', fontName='Helvetica-Bold',
                                           fontSize=11, textColor=WHITE,
                                           alignment=TA_CENTER)
            t = Table([[Paragraph(section_name, heading_style)]], colWidths=[17*cm])
            t.setStyle(TableStyle([
                ('BACKGROUND',    (0,0),(-1,-1), ACCENT),
                ('TOPPADDING',    (0,0),(-1,-1), 6),
                ('BOTTOMPADDING', (0,0),(-1,-1), 6),
            ]))
            story.append(t)
            story.append(Spacer(1, 6))

        q_style = ParagraphStyle('q', fontName='Helvetica', fontSize=10,
                                 textColor=BLACK, leading=15, alignment=TA_JUSTIFY)
        n_style = ParagraphStyle('n', fontName='Helvetica-Bold', fontSize=10,
                                 textColor=ACCENT)
        m_style = ParagraphStyle('m', fontName='Helvetica-Bold', fontSize=9,
                                 textColor=MID_GRAY, alignment=TA_RIGHT)

        for i, q in enumerate(questions, 1):
            qtext = q.get('text', '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            tags  = []
            if q.get('co'):  tags.append(q['co'])
            if q.get('bl'):  tags.append(q['bl'].capitalize())
            tag_str = '  '.join(tags)
            tag_para = Paragraph(
                f'<font color="#8a8fa8" size="8">{tag_str}</font>',
                ParagraphStyle('t', fontName='Helvetica', fontSize=8)
            )
            row = Table(
                [[Paragraph(f'{i}.', n_style),
                  Table([[Paragraph(qtext, q_style)],[tag_para]], colWidths=[13*cm]),
                  Paragraph(f'[{mpq}M]', m_style)]],
                colWidths=[0.8*cm, 13.5*cm, 2.2*cm]
            )
            row.setStyle(TableStyle([
                ('VALIGN',        (0,0),(-1,-1), 'TOP'),
                ('LEFTPADDING',   (0,0),(-1,-1), 3),
                ('RIGHTPADDING',  (0,0),(-1,-1), 3),
                ('TOPPADDING',    (0,0),(-1,-1), 4),
                ('BOTTOMPADDING', (0,0),(-1,-1), 5),
                ('BACKGROUND',    (0,0),(-1,-1),
                 LIGHT_GRAY if i % 2 == 0 else WHITE),
            ]))
            story.append(KeepTogether(row))

        story.append(Spacer(1, 10))


def export_editor_pdf(blocks: list, title: str = 'Question Paper') -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm,  bottomMargin=2*cm,
                            title=title)
    story = []
    for block in blocks:
        _process_block(block, story)

    if not story:
        story.append(Paragraph('Empty paper', ParagraphStyle('e', fontSize=12)))

    doc.build(story)
    buf.seek(0)
    return buf
