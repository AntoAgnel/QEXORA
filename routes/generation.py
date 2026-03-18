from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models.paper_template import PaperTemplate
from models.question_paper import QuestionPaper
from services.question_selector import select_questions_for_template
from services.pdf_exporter import generate_paper_pdf
import re

generation_bp = Blueprint('generation', __name__)

@generation_bp.route('/')
@login_required
def index():
    inst = current_user.institution_type
    templates = PaperTemplate.get_all(inst)
    return render_template('generation/index.html', templates=templates)

@generation_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    template_id = request.form.get('template_id')
    title       = request.form.get('title', 'Question Paper')
    subject     = request.form.get('subject', '')

    template = PaperTemplate.get_by_id(template_id)
    if not template:
        flash('Template not found.', 'danger')
        return redirect(url_for('generation.index'))

    result = select_questions_for_template(
        template,
        current_user.institution_type,
        subject or None
    )

    paper_data = {
        'title':            title,
        'subject':          subject,
        'institution_type': current_user.institution_type,
        'template_id':      template_id,
        'sections':         result['sections'],
        'total_marks':      result['total_marks'],
        'analytics':        result['analytics'],
        'created_by':       current_user.id
    }
    paper_id = QuestionPaper.create(paper_data)
    return redirect(url_for('generation.preview', paper_id=paper_id))

@generation_bp.route('/preview/<paper_id>')
@login_required
def preview(paper_id):
    paper = QuestionPaper.get_by_id(paper_id)
    if not paper:
        flash('Question paper not found.', 'danger')
        return redirect(url_for('generation.index'))
    return render_template('generation/preview.html', paper=paper)

@generation_bp.route('/export/<paper_id>/pdf')
@login_required
def export_pdf(paper_id):
    paper = QuestionPaper.get_by_id(paper_id)
    if not paper:
        flash('Question paper not found.', 'danger')
        return redirect(url_for('generation.index'))

    pdf_buf = generate_paper_pdf(paper)

    # Safe filename from paper title
    safe_title = re.sub(r'[^\w\s-]', '', paper.get('title', 'question_paper'))
    safe_title = re.sub(r'\s+', '_', safe_title.strip())
    filename   = f"{safe_title}.pdf"

    return send_file(
        pdf_buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@generation_bp.route('/delete/<paper_id>', methods=['POST'])
@login_required
def delete(paper_id):
    QuestionPaper.delete(paper_id)
    flash('Paper deleted.', 'success')
    return redirect(url_for('dashboard.index'))
