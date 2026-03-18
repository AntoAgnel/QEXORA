"""
PDF Export Service for QEXORA
Generates a professional, print-ready question paper PDF using ReportLab.
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)


# ── Colour palette ────────────────────────────────────────────────────────────
DARK       = colors.HexColor('#0e0f14')
ACCENT     = colors.HexColor('#6c63ff')
ACCENT2    = colors.HexColor('#00d4aa')
LIGHT_GRAY = colors.HexColor('#f4f4f8')
MID_GRAY   = colors.HexColor('#8a8fa8')
WHITE      = colors.white
BLACK      = colors.black

EASY_COLOR   = colors.HexColor('#00d4aa')
MEDIUM_COLOR = colors.HexColor('#f5a623')
HARD_COLOR   = colors.HexColor('#ff6b6b')


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        'institution': ParagraphStyle(
            'institution',
            fontName='Helvetica-Bold', fontSize=10,
            textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=2
        ),
        'exam_title': ParagraphStyle(
            'exam_title',
            fontName='Helvetica-Bold', fontSize=16,
            textColor=BLACK, alignment=TA_CENTER, spaceAfter=4
        ),
        'exam_meta': ParagraphStyle(
            'exam_meta',
            fontName='Helvetica', fontSize=9,
            textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=2
        ),
        'section_heading': ParagraphStyle(
            'section_heading',
            fontName='Helvetica-Bold', fontSize=11,
            textColor=WHITE, alignment=TA_CENTER,
            spaceBefore=14, spaceAfter=6,
            leftIndent=0, rightIndent=0
        ),
        'section_instruction': ParagraphStyle(
            'section_instruction',
            fontName='Helvetica-Oblique', fontSize=8.5,
            textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=8
        ),
        'question': ParagraphStyle(
            'question',
            fontName='Helvetica', fontSize=10,
            textColor=BLACK, alignment=TA_JUSTIFY,
            leading=15, spaceAfter=4
        ),
        'question_num': ParagraphStyle(
            'question_num',
            fontName='Helvetica-Bold', fontSize=10,
            textColor=ACCENT, alignment=TA_LEFT
        ),
        'mapping_tag': ParagraphStyle(
            'mapping_tag',
            fontName='Helvetica', fontSize=7.5,
            textColor=MID_GRAY, alignment=TA_RIGHT
        ),
        'analytics_heading': ParagraphStyle(
            'analytics_heading',
            fontName='Helvetica-Bold', fontSize=10,
            textColor=BLACK, spaceBefore=12, spaceAfter=6
        ),
        'footer': ParagraphStyle(
            'footer',
            fontName='Helvetica', fontSize=7.5,
            textColor=MID_GRAY, alignment=TA_CENTER
        ),
    }
    return styles


def _header_table(paper: dict, styles: dict):
    """Build the exam header block."""
    inst_type = paper.get('institution_type', '').replace('_', ' ').title()
    title     = paper.get('title', 'Question Paper')
    subject   = paper.get('subject', '')
    total_m   = paper.get('total_marks', 0)
    date_str  = paper.get('created_at', '').strftime('%d %B %Y') if hasattr(paper.get('created_at', ''), 'strftime') else ''

    content = [
        Paragraph(inst_type, styles['institution']),
        Paragraph(title, styles['exam_title']),
    ]

    meta_parts = []
    if subject:   meta_parts.append(f"Subject: {subject}")
    if total_m:   meta_parts.append(f"Total Marks: {total_m}")
    if date_str:  meta_parts.append(f"Date: {date_str}")

    if meta_parts:
        content.append(Paragraph("  |  ".join(meta_parts), styles['exam_meta']))

    return content


def _section_block(section: dict, sec_index: int, styles: dict):
    """Build one section's worth of flowables."""
    flowables = []
    sec_name  = section.get('section_name', f'Section {sec_index}')
    q_type    = section.get('question_type', 'short').capitalize()
    mpq       = section.get('marks_per_question', 2)
    questions = section.get('questions', [])

    # Section heading bar
    heading_table = Table(
        [[Paragraph(sec_name, styles['section_heading'])]],
        colWidths=[17 * cm]
    )
    heading_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
    ]))
    flowables.append(heading_table)

    instruction = f"({q_type} Answer Questions — {mpq} Mark{'s' if mpq != 1 else ''} each)"
    flowables.append(Paragraph(instruction, styles['section_instruction']))

    if not questions:
        flowables.append(
            Paragraph("No questions available for this section.", styles['question'])
        )
        flowables.append(Spacer(1, 6))
        return flowables

    for i, q in enumerate(questions, 1):
        # Build question row: [num | text | marks+mapping]
        num_para  = Paragraph(f"{i}.", styles['question_num'])
        q_text    = q.get('text', '')
        q_para    = Paragraph(q_text, styles['question'])

        # Mapping tags
        tags = []
        if q.get('co'):  tags.append(q['co'])
        if q.get('bl'):  tags.append(q['bl'].capitalize())
        if q.get('kc'):  tags.append(q['kc'].capitalize())
        marks_line = f"[{mpq}M]"
        tag_line   = "  ".join(tags) if tags else ""
        mapping_para = Paragraph(
            f"<b>{marks_line}</b><br/><font color='#8a8fa8'>{tag_line}</font>",
            styles['mapping_tag']
        )

        row = Table(
            [[num_para, q_para, mapping_para]],
            colWidths=[1 * cm, 13.5 * cm, 2.5 * cm]
        )
        row.setStyle(TableStyle([
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',   (0, 0), (-1, -1), 4),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 4),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        # Alternate row shading
        if i % 2 == 0:
            row.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
            ]))

        flowables.append(KeepTogether(row))

    flowables.append(Spacer(1, 8))
    return flowables


def _analytics_block(analytics: dict, styles: dict):
    """Build the CO / BL / difficulty analytics table at the end."""
    flowables = []
    flowables.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e0e0e8'), spaceAfter=8))
    flowables.append(Paragraph("Outcome Coverage Summary", styles['analytics_heading']))

    co_cov  = analytics.get('co_coverage', {})
    bl_dist = analytics.get('bl_distribution', {})
    diff    = analytics.get('difficulty_distribution', {})
    total   = analytics.get('total_questions', 1) or 1

    # CO table
    if co_cov:
        rows = [['Course Outcome', 'Questions', '% Coverage']]
        for co, cnt in sorted(co_cov.items()):
            rows.append([co, str(cnt), f"{cnt/total*100:.0f}%"])
        t = Table(rows, colWidths=[6 * cm, 4 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0),  ACCENT),
            ('TEXTCOLOR',    (0, 0), (-1, 0),  WHITE),
            ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',     (0, 0), (-1, -1), 8.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, WHITE]),
            ('ALIGN',        (1, 0), (-1, -1), 'CENTER'),
            ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d8')),
            ('TOPPADDING',   (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ]))
        flowables.append(t)
        flowables.append(Spacer(1, 10))

    # BL + Difficulty side by side
    if bl_dist or diff:
        left_rows = [["Bloom's Level", "Count"]]
        for lvl, cnt in bl_dist.items():
            left_rows.append([lvl.capitalize(), str(cnt)])

        right_rows = [["Difficulty", "Count", "%"]]
        for d, cnt in diff.items():
            right_rows.append([d.capitalize(), str(cnt), f"{cnt/total*100:.0f}%"])

        def mini_table(rows):
            t = Table(rows, colWidths=[3.5 * cm, 2 * cm, 2 * cm][:len(rows[0])])
            t.setStyle(TableStyle([
                ('BACKGROUND',   (0, 0), (-1, 0),  ACCENT2),
                ('TEXTCOLOR',    (0, 0), (-1, 0),  WHITE),
                ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
                ('FONTSIZE',     (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GRAY, WHITE]),
                ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#d0d0d8')),
                ('TOPPADDING',   (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
            ]))
            return t

        combo = Table(
            [[mini_table(left_rows), mini_table(right_rows)]],
            colWidths=[8.5 * cm, 8.5 * cm]
        )
        combo.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING',  (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        flowables.append(combo)

    return flowables


def generate_paper_pdf(paper: dict) -> BytesIO:
    """
    Given a question paper document (dict from MongoDB),
    returns a BytesIO buffer containing the PDF.
    """
    buf    = BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2 * cm,
        title=paper.get('title', 'Question Paper'),
        author='QEXORA',
        subject=paper.get('subject', ''),
    )

    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.extend(_header_table(paper, styles))
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT, spaceAfter=12))

    # ── Sections ──────────────────────────────────────────────────────────────
    for idx, section in enumerate(paper.get('sections', []), 1):
        story.extend(_section_block(section, idx, styles))

    # ── Analytics ─────────────────────────────────────────────────────────────
    analytics = paper.get('analytics', {})
    if analytics.get('co_coverage') or analytics.get('bl_distribution'):
        story.extend(_analytics_block(analytics, styles))

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "Generated by QEXORA – Intelligent Academic Mapping & Question Paper Generation System",
        styles['footer']
    ))

    doc.build(story)
    buf.seek(0)
    return buf
