import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.paper_template import PaperTemplate

templates_bp = Blueprint('paper_templates', __name__)

@templates_bp.route('/')
@login_required
def index():
    inst = current_user.institution_type
    templates = PaperTemplate.get_all(inst)
    return render_template('paper_templates/list.html', templates=templates)

@templates_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        sections_raw = request.form.get('sections_json', '[]')
        try:
            sections = json.loads(sections_raw)
        except Exception:
            sections = []

        data = {
            'name':             request.form.get('name', ''),
            'institution_type': current_user.institution_type,
            'subject':          request.form.get('subject', ''),
            'total_marks':      request.form.get('total_marks', 100),
            'sections':         sections,
            'is_default':       False,
            'created_by':       current_user.id
        }
        PaperTemplate.create(data)
        flash('Template created successfully.', 'success')
        return redirect(url_for('paper_templates.index'))

    return render_template('paper_templates/create.html')

@templates_bp.route('/delete/<template_id>', methods=['POST'])
@login_required
def delete(template_id):
    PaperTemplate.delete(template_id)
    flash('Template deleted.', 'success')
    return redirect(url_for('paper_templates.index'))
