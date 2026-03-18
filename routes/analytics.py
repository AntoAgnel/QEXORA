from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.question_paper import QuestionPaper
from models.question import Question

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def index():
    papers  = QuestionPaper.get_all(current_user.id)
    inst    = current_user.institution_type

    # Aggregate CO attainment across all papers
    co_attainment = {}
    bl_total      = {}
    diff_total    = {'easy': 0, 'medium': 0, 'hard': 0}

    for paper in papers:
        analytics = paper.get('analytics', {})
        for co, count in analytics.get('co_coverage', {}).items():
            co_attainment[co] = co_attainment.get(co, 0) + count
        for bl, count in analytics.get('bl_distribution', {}).items():
            bl_total[bl] = bl_total.get(bl, 0) + count
        for d, count in analytics.get('difficulty_distribution', {}).items():
            diff_total[d] = diff_total.get(d, 0) + count

    return render_template('analytics/index.html',
                           papers=papers,
                           co_attainment=co_attainment,
                           bl_total=bl_total,
                           diff_total=diff_total)
