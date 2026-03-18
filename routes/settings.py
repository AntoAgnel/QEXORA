from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.user import User

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
def index():
    return render_template('settings/index.html', active='profile')

@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    data = {
        'name':       request.form.get('name', '').strip(),
        'phone':      request.form.get('phone', '').strip(),
        'department': request.form.get('department', '').strip(),
        'bio':        request.form.get('bio', '').strip(),
    }
    if not data['name']:
        flash('Name cannot be empty.', 'danger')
        return redirect(url_for('settings.index'))
    User.update_profile(current_user.id, data)
    flash('Profile updated successfully.', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    from extensions import mongo
    from bson import ObjectId
    current_pw  = request.form.get('current_password', '')
    new_pw      = request.form.get('new_password', '')
    confirm_pw  = request.form.get('confirm_password', '')

    user_doc = mongo.db.users.find_one({'_id': ObjectId(current_user.id)})

    # Google-only accounts have no password
    if not user_doc.get('password'):
        flash('Your account uses Google Sign-In. Set a password first via Forgot Password.', 'info')
        return redirect(url_for('settings.index') + '#security')

    if not User.check_password(user_doc['password'], current_pw):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('settings.index') + '#security')
    if len(new_pw) < 8:
        flash('New password must be at least 8 characters.', 'danger')
        return redirect(url_for('settings.index') + '#security')
    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('settings.index') + '#security')

    User.update_password(current_user.id, new_pw)
    flash('Password changed successfully.', 'success')
    return redirect(url_for('settings.index') + '#security')

@settings_bp.route('/institution', methods=['POST'])
@login_required
def update_institution():
    inst  = request.form.get('institution_type', '')
    valid = ['engineering', 'arts_science', 'school']
    if inst not in valid:
        flash('Invalid institution type.', 'danger')
        return redirect(url_for('settings.index') + '#institution')
    User.update_institution(current_user.id, inst)
    flash('Institution type updated.', 'success')
    return redirect(url_for('settings.index') + '#institution')
