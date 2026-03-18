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

@dashboard_bp.route('/run-seed')
def run_seed():
    from extensions import mongo
    from models.paper_template import PaperTemplate
    from datetime import datetime
    
    try:
        # Seed templates
        PaperTemplate.seed_defaults()
        
        # Check questions
        total = mongo.db.questions.count_documents({})
        if total > 0:
            return f"✓ Already seeded! Total questions: {total}"
        
        # Seed questions
        from seed_db import ENGINEERING_QUESTIONS, ARTS_SCIENCE_QUESTIONS, SCHOOL_QUESTIONS, ALL_DATA
        seeded = 0
        for inst_type, questions in ALL_DATA:
            docs = []
            for q in questions:
                doc = dict(q)
                doc['institution_type'] = inst_type
                doc['created_by'] = 'seed'
                doc['created_at'] = datetime.utcnow()
                for field in ['co','bl','kc','pi','po','pso','chapter','learning_outcome']:
                    doc.setdefault(field, '')
                docs.append(doc)
            mongo.db.questions.insert_many(docs)
            seeded += len(docs)
        
        return f"✓ Seeded successfully! {seeded} questions added."
    except Exception as e:
        return f"✗ Error: {str(e)}"