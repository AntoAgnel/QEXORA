from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.question import Question
from models.paper_template import PaperTemplate
from models.question_paper import QuestionPaper
from extensions import mongo

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    inst = current_user.institution_type
    stats = {
        'total_questions': Question.count({'institution_type': inst}),
        'total_templates': len(PaperTemplate.get_all(inst)),
        'total_papers':    len(QuestionPaper.get_all(current_user.id)),
        'recent_papers':   QuestionPaper.get_all(current_user.id)[:5]
    }
    return render_template('dashboard/index.html', stats=stats)
