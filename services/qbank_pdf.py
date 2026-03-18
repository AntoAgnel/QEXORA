"""
Question Bank PDF Generator
Produces a clean, student-friendly question bank PDF for study reference.
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

ACCENT      = colors.HexColor('#6c63ff')
ACCENT2     = colors.HexColor('#00d4aa')
LIGHT_GRAY  = colors.HexColor('#f4f4f8')
MID_GRAY    = colors.HexColor('#8a8fa8')
EASY_COL    = colors.HexColor('#00d4aa')
MEDIUM_COL  = colors.HexColor('#f5a623')
HARD_COL    = colors.HexColor('#ff6b6b')
BLACK       = colors.black
WHITE       = colors.white

DIFF_COLOR = {'easy': EASY_COL, 'medium': MEDIUM_COL, 'hard': HARD_COL}


def _styles():
    return {
        'title': ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=18,
                                textColor=BLACK, alignment=TA_CENTER, spaceAfter=4),
        'subtitle': ParagraphStyle('subtitle', fontName='Helvetica', fontSize=10,
                                   textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=2),
        'section': ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=11,
                                  textColor=WHITE, alignment=TA_LEFT),
        'q_num': ParagraphStyle('q_num', fontName='Helvetica-Bold', fontSize=10,
                                textColor=ACCENT),
        'q_text': ParagraphStyle('q_text', fontName='Helvetica', fontSize=10,
                                 textColor=BLACK, leading=15, alignment=TA_JUSTIFY),
        'tag': ParagraphStyle('tag', fontName='Helvetica', fontSize=8,
                              textColor=MID_GRAY, alignment=TA_LEFT),
        'footer': ParagraphStyle('footer', fontName='Helvetica', fontSize=7.5,
                                 textColor=MID_GRAY, alignment=TA_CENTER),
    }


def generate_qbank_pdf(questions: list, institution_type: str, faculty_name: str = '') -> BytesIO:
    buf  = BytesIO()
    st   = _styles()
    date = datetime.now().strftime('%d %B %Y')
    inst_label = institution_type.replace('_', ' ').title()

    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2.2*cm, bottomMargin=2*cm,
                            title='Question Bank')
    story = []

    # ── Cover header ──────────────────────────────────────────────────────
    story.append(Paragraph('QEXORA', ParagraphStyle('brand', fontName='Helvetica-Bold',
                  fontSize=11, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph('Question Bank', st['title']))
    story.append(Paragraph(
        f"{inst_label}  |  {len(questions)} Questions  |  {date}",
        st['subtitle']
    ))
    if faculty_name:
        story.append(Paragraph(f"Prepared by: {faculty_name}", st['subtitle']))
    story.append(HRFlowable(width='100%', thickness=2, color=ACCENT, spaceAfter=16))

    # ── Group by subject ──────────────────────────────────────────────────
    subjects = {}
    for q in questions:
        subj = q.get('subject', 'General')
        subjects.setdefault(subj, []).append(q)

    global_num = 1
    for subj, qs in subjects.items():
        # Subject heading bar
        heading = Table([[Paragraph(subj, st['section'])]],
                        colWidths=[17*cm])
        heading.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), ACCENT),
            ('TOPPADDING',    (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 7),
            ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ]))
        story.append(heading)
        story.append(Spacer(1, 8))

        for q in qs:
            diff  = q.get('difficulty', 'medium')
            marks = q.get('marks', 2)
            co    = q.get('co', '')
            bl    = q.get('bl', '')
            unit  = q.get('unit', '')

            # Build tag line
            tags = []
            if unit:  tags.append(f"Unit: {unit}")
            if co:    tags.append(co)
            if bl:    tags.append(bl.capitalize())
            tag_text = '  •  '.join(tags) if tags else ''

            num_p  = Paragraph(f"Q{global_num}.", st['q_num'])
            text_p = Paragraph(q.get('text', ''), st['q_text'])
            mark_p = Paragraph(
                f"[{marks}M]",
                ParagraphStyle('m', fontName='Helvetica-Bold', fontSize=9,
                               textColor=DIFF_COLOR.get(diff, MID_GRAY), alignment=TA_LEFT)
            )
            tag_p  = Paragraph(tag_text, st['tag'])

            row = Table(
                [[num_p, Table([[text_p],[tag_p]], colWidths=[13*cm]),  mark_p]],
                colWidths=[1*cm, 13.5*cm, 2.5*cm]
            )
            row.setStyle(TableStyle([
                ('VALIGN',        (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING',   (0,0), (-1,-1), 4),
                ('RIGHTPADDING',  (0,0), (-1,-1), 4),
                ('TOPPADDING',    (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('BACKGROUND',    (0,0), (-1,-1),
                 LIGHT_GRAY if global_num % 2 == 0 else WHITE),
            ]))
            story.append(KeepTogether(row))
            global_num += 1

        story.append(Spacer(1, 12))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1,
                             color=colors.HexColor('#e0e0e8'), spaceAfter=8))
    story.append(Paragraph(
        f"Generated by QEXORA — For Academic Reference Only — {date}",
        st['footer']
    ))

    doc.build(story)
    buf.seek(0)
    return buf
