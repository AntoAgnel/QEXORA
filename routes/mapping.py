from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.question import Question

mapping_bp = Blueprint('mapping', __name__)

@mapping_bp.route('/')
@login_required
def index():
    inst      = current_user.institution_type
    questions = Question.get_all(inst)
    return render_template('mapping/index.html', questions=questions, inst=inst)

@mapping_bp.route('/update/<question_id>', methods=['POST'])
@login_required
def update(question_id):
    data = request.form.to_dict()
    mapping_fields = ['co','bl','kc','pi','po','pso','learning_outcome','chapter','difficulty']
    update_data = {k: v for k, v in data.items() if k in mapping_fields}
    Question.update(question_id, update_data)
    flash('Mapping updated successfully.', 'success')
    return redirect(url_for('mapping.index'))

@mapping_bp.route('/bulk-update', methods=['POST'])
@login_required
def bulk_update():
    """Apply same mapping values to multiple selected questions."""
    data    = request.json or {}
    ids     = data.get('ids', [])
    mapping = data.get('mapping', {})
    allowed = ['co','bl','kc','pi','po','pso','learning_outcome','chapter','difficulty']
    clean   = {k: v for k, v in mapping.items() if k in allowed and v}
    if not ids or not clean:
        return jsonify({'success': False, 'message': 'No questions or mapping provided'}), 400
    for qid in ids:
        Question.update(qid, clean)
    return jsonify({'success': True, 'updated': len(ids)})
