from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.question import Question
from models.question_paper import QuestionPaper
from extensions import mongo
from functools import wraps

dev_bp = Blueprint('dev', __name__)

def superadmin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superadmin:
            flash('Access denied. Developer only.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated

@dev_bp.route('/')
@login_required
@superadmin_required
def index():
    users     = User.get_all()
    stats = {
        'total_users':     len(users),
        'total_questions': mongo.db.questions.count_documents({}),
        'total_papers':    mongo.db.question_papers.count_documents({}),
        'total_templates': mongo.db.templates.count_documents({}),
        'by_institution':  {
            'engineering':  mongo.db.questions.count_documents({'institution_type': 'engineering'}),
            'arts_science': mongo.db.questions.count_documents({'institution_type': 'arts_science'}),
            'school':       mongo.db.questions.count_documents({'institution_type': 'school'}),
        }
    }
    return render_template('dev/index.html', users=users, stats=stats)

@dev_bp.route('/update-role', methods=['POST'])
@login_required
@superadmin_required
def update_role():
    user_id = request.form.get('user_id')
    role    = request.form.get('role')
    valid_roles = ['faculty', 'admin', 'superadmin']
    if role not in valid_roles:
        flash('Invalid role.', 'danger')
        return redirect(url_for('dev.index'))
    User.update_role(user_id, role)
    flash('Role updated successfully.', 'success')
    return redirect(url_for('dev.index'))

@dev_bp.route('/update-institution', methods=['POST'])
@login_required
@superadmin_required
def update_institution():
    user_id = request.form.get('user_id')
    inst    = request.form.get('institution_type')
    valid   = ['engineering', 'arts_science', 'school']
    if inst not in valid:
        flash('Invalid institution type.', 'danger')
        return redirect(url_for('dev.index'))
    User.update_institution(user_id, inst)
    flash('Institution updated.', 'success')
    return redirect(url_for('dev.index'))

@dev_bp.route('/delete-user/<user_id>', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Cannot delete your own account.', 'danger')
        return redirect(url_for('dev.index'))
    User.delete(user_id)
    flash('User deleted.', 'success')
    return redirect(url_for('dev.index'))
