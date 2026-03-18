from flask import (Blueprint, render_template, request, jsonify,
                   redirect, url_for, flash, send_file)
from flask_login import login_required, current_user
from models.question_paper import QuestionPaper
from extensions import mongo
from bson import ObjectId
from datetime import datetime
from services.editor_export import export_editor_pdf
import json, re

editor_bp = Blueprint('editor', __name__)


def _sanitize(obj):
    """Recursively convert ObjectId, datetime and other non-serializable types to strings/plain dicts."""
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(i) for i in obj]
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.strftime('%d %B %Y')
    return obj


@editor_bp.route('/<paper_id>')
@login_required
def index(paper_id):
    paper = QuestionPaper.get_by_id(paper_id)
    if not paper:
        flash('Question paper not found.', 'danger')
        return redirect(url_for('dashboard.index'))

    # Deep-sanitize the entire document so tojson works perfectly
    paper = _sanitize(paper)
    return render_template('editor/index.html', paper=paper)


@editor_bp.route('/save/<paper_id>', methods=['POST'])
@login_required
def save(paper_id):
    data   = request.json or {}
    blocks = data.get('blocks', [])
    mongo.db.question_papers.update_one(
        {'_id': ObjectId(paper_id)},
        {'$set': {'editor_blocks': blocks, 'editor_updated': datetime.utcnow()}}
    )
    return jsonify({'success': True, 'saved': len(blocks)})


@editor_bp.route('/export/<paper_id>/pdf', methods=['POST'])
@login_required
def export_pdf(paper_id):
    data   = request.json or {}
    blocks = data.get('blocks', [])
    title  = data.get('title', 'Question Paper')
    buf      = export_editor_pdf(blocks, title)
    safe     = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    filename = f"{safe}_edited.pdf"
    return send_file(buf, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)


@editor_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    data     = request.json or {}
    img_data = data.get('data', '')
    if not img_data:
        return jsonify({'success': False}), 400
    return jsonify({'success': True, 'src': img_data})