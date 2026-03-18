from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, session, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from services.email_service import send_otp_email, send_welcome_email
import requests as req

auth_bp = Blueprint('auth', __name__)

# ── Register ─────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.register'))
        if User.find_by_email(email):
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
        User.create(name, email, password)
        try:
            send_welcome_email(email, name)
        except Exception:
            pass
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        user_doc = User.find_by_email(email)
        if user_doc and User.check_password(user_doc['password'], password):
            user = User(user_doc)
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# ── Google OAuth ──────────────────────────────────────────────────────────────
@auth_bp.route('/google')
def google_login():
    client_id    = current_app.config.get('GOOGLE_CLIENT_ID', '')
    redirect_uri = url_for('auth.google_callback', _external=True)
    if not client_id:
        flash('Google login is not configured yet.', 'danger')
        return redirect(url_for('auth.login'))
    scope = 'openid email profile'
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
    )
    return redirect(auth_url)


@auth_bp.route('/google/callback')
def google_callback():
    code         = request.args.get('code')
    client_id    = current_app.config.get('GOOGLE_CLIENT_ID', '')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET', '')
    redirect_uri = url_for('auth.google_callback', _external=True)

    if not code or not client_id:
        flash('Google login failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    # Exchange code for token
    token_resp = req.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    })
    token_data = token_resp.json()
    access_token = token_data.get('access_token')
    if not access_token:
        flash('Google authentication failed.', 'danger')
        return redirect(url_for('auth.login'))

    # Get user info
    info_resp = req.get('https://www.googleapis.com/oauth2/v2/userinfo',
                        headers={'Authorization': f'Bearer {access_token}'})
    info = info_resp.json()
    google_id = info.get('id', '')
    email     = info.get('email', '').lower()
    name      = info.get('name', '')
    avatar    = info.get('picture', '')

    if not email:
        flash('Could not retrieve email from Google.', 'danger')
        return redirect(url_for('auth.login'))

    # Find or create user
    user_doc = User.find_by_email(email)
    if not user_doc:
        User.create(name, email, password=None, google_id=google_id)
        user_doc = User.find_by_email(email)
        # Save avatar
        from bson import ObjectId
        from extensions import mongo
        mongo.db.users.update_one({'_id': user_doc['_id']},
                                  {'$set': {'avatar': avatar, 'google_id': google_id}})

    user = User(user_doc)
    login_user(user)
    return redirect(url_for('dashboard.index'))


# ── Forgot Password ───────────────────────────────────────────────────────────
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        user_doc = User.find_by_email(email)
        if user_doc:
            otp  = User.set_otp(email)
            sent = send_otp_email(email, user_doc.get('name', 'User'), otp)
            if sent:
                session['reset_email'] = email
                flash('OTP sent to your email. Check your inbox.', 'success')
                return redirect(url_for('auth.verify_otp'))
            else:
                flash('Failed to send email. Check your MAIL settings in .env', 'danger')
        else:
            # Don't reveal if email exists
            flash('If this email is registered, an OTP has been sent.', 'info')
            session['reset_email'] = email
            return redirect(url_for('auth.verify_otp'))
    return render_template('auth/forgot_password.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_email', '')
    if not email:
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        ok, msg = User.verify_otp(email, otp)
        if ok:
            session['otp_verified'] = True
            return redirect(url_for('auth.reset_password'))
        flash(msg, 'danger')
    return render_template('auth/verify_otp.html', email=email)


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('reset_email', '')
    if not email:
        return jsonify({'success': False}), 400
    user_doc = User.find_by_email(email)
    if user_doc:
        otp = User.set_otp(email)
        send_otp_email(email, user_doc.get('name', 'User'), otp)
    return jsonify({'success': True})


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified'):
        return redirect(url_for('auth.forgot_password'))
    email = session.get('reset_email', '')
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.reset_password'))
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password'))
        user_doc = User.find_by_email(email)
        if user_doc:
            User.update_password(str(user_doc['_id']), password)
            session.pop('reset_email', None)
            session.pop('otp_verified', None)
            flash('Password reset successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')


# ── Institution update (AJAX) ─────────────────────────────────────────────────
@auth_bp.route('/update-institution', methods=['POST'])
@login_required
def update_institution():
    inst  = request.json.get('institution_type', '')
    valid = ['engineering', 'arts_science', 'school']
    if inst not in valid:
        return jsonify({'success': False, 'message': 'Invalid institution type'}), 400
    User.update_institution(current_user.id, inst)
    return jsonify({'success': True, 'institution_type': inst})
