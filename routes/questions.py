from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from models.question import Question
from services.ai_mapping import suggest_mapping, get_pi_codes
from services.qbank_pdf import generate_qbank_pdf
import json

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/')
@login_required
def index():
    inst = current_user.institution_type
    questions = Question.get_all(inst)
    return render_template('questions/list.html', questions=questions)

@questions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['institution_type'] = current_user.institution_type
        data['created_by'] = current_user.id
        Question.create(data)
        flash('Question added successfully.', 'success')
        return redirect(url_for('questions.index'))
    return render_template('questions/add.html', pi_codes=get_pi_codes())

@questions_bp.route('/edit/<question_id>', methods=['GET', 'POST'])
@login_required
def edit(question_id):
    q = Question.get_by_id(question_id)
    if not q:
        flash('Question not found.', 'danger')
        return redirect(url_for('questions.index'))
    if request.method == 'POST':
        data = request.form.to_dict()
        Question.update(question_id, data)
        flash('Question updated.', 'success')
        return redirect(url_for('questions.index'))
    return render_template('questions/edit.html', question=q, pi_codes=get_pi_codes())

@questions_bp.route('/delete/<question_id>', methods=['POST'])
@login_required
def delete(question_id):
    Question.delete(question_id)
    flash('Question deleted.', 'success')
    return redirect(url_for('questions.index'))

@questions_bp.route('/delete-multiple', methods=['POST'])
@login_required
def delete_multiple():
    ids = request.json.get('ids', [])
    for qid in ids:
        Question.delete(qid)
    return jsonify({'success': True, 'deleted': len(ids)})

@questions_bp.route('/ai-suggest', methods=['POST'])
@login_required
def ai_suggest():
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    result = suggest_mapping(text, current_user.institution_type)
    return jsonify(result)

@questions_bp.route('/pi-codes')
@login_required
def pi_codes():
    return jsonify(get_pi_codes())

@questions_bp.route('/export/pdf')
@login_required
def export_pdf():
    """Export selected or all questions as a PDF for students."""
    ids  = request.args.get('ids', '')
    inst = current_user.institution_type
    if ids:
        id_list   = ids.split(',')
        questions = [Question.get_by_id(qid) for qid in id_list if Question.get_by_id(qid)]
    else:
        questions = Question.get_all(inst)

    if not questions:
        flash('No questions to export.', 'danger')
        return redirect(url_for('questions.index'))

    buf      = generate_qbank_pdf(questions, inst, current_user.name)
    filename = f"Question_Bank_{inst.replace('_','-')}.pdf"
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)
