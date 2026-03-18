import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, session
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    MONGO_URI = os.environ.get('MONGO_URI', '')
    print(f"[STARTUP] MONGO_URI: {'YES' if MONGO_URI else 'EMPTY!'}")

    app.config['SECRET_KEY']          = os.environ.get('SECRET_KEY', 'qexora-key')
    app.config['MONGO_URI']           = MONGO_URI
    app.config['DEBUG']               = False
    app.config['MAIL_SERVER']         = 'smtp.gmail.com'
    app.config['MAIL_PORT']           = 587
    app.config['MAIL_USE_TLS']        = True
    app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_APP_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')
    app.permanent_session_lifetime    = timedelta(seconds=1800)

    from extensions import mongo, bcrypt, login_manager, mail
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view             = 'auth.login'
    login_manager.login_message_category = 'info'

    from bson import ObjectId
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        try:
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user) if user else None
        except Exception as e:
            print(f"[USER_LOADER] Error: {e}")
            return None

    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # Auto-seed
    try:
        from models.paper_template import PaperTemplate
        from datetime import datetime
        PaperTemplate.seed_defaults()
        total = mongo.db.questions.count_documents({})
        if total == 0:
            _seed_questions(mongo, datetime)
        else:
            print(f"[SEED] ✓ Already has {total} questions")
    except Exception as e:
        print(f"[SEED] ✗ {e}")

    from routes.auth            import auth_bp
    from routes.dashboard       import dashboard_bp
    from routes.questions       import questions_bp
    from routes.mapping         import mapping_bp
    from routes.paper_templates import templates_bp
    from routes.generation      import generation_bp
    from routes.analytics       import analytics_bp
    from routes.dev             import dev_bp
    from routes.settings        import settings_bp
    from routes.editor          import editor_bp

    app.register_blueprint(auth_bp,       url_prefix='/auth')
    app.register_blueprint(dashboard_bp,  url_prefix='/')
    app.register_blueprint(questions_bp,  url_prefix='/questions')
    app.register_blueprint(mapping_bp,    url_prefix='/mapping')
    app.register_blueprint(templates_bp,  url_prefix='/templates')
    app.register_blueprint(generation_bp, url_prefix='/generate')
    app.register_blueprint(analytics_bp,  url_prefix='/analytics')
    app.register_blueprint(dev_bp,        url_prefix='/dev')
    app.register_blueprint(settings_bp,   url_prefix='/settings')
    app.register_blueprint(editor_bp,     url_prefix='/editor')

    print("[STARTUP] ✓ App ready")
    return app


def _seed_questions(mongo, datetime):
    QUESTIONS = {
        'engineering': [
            dict(text="Define data structure and list its types.", subject="Data Structures", unit="Unit 1", marks=2, difficulty="easy", co="CO1", bl="remember", kc="factual", pi="PI1.1"),
            dict(text="State the LIFO principle used in stack operations.", subject="Data Structures", unit="Unit 1", marks=2, difficulty="easy", co="CO1", bl="remember", kc="factual", pi="PI1.1"),
            dict(text="List the differences between stack and queue.", subject="Data Structures", unit="Unit 1", marks=2, difficulty="easy", co="CO1", bl="remember", kc="conceptual", pi="PI1.2"),
            dict(text="Explain the working of a circular queue with a suitable example.", subject="Data Structures", unit="Unit 1", marks=6, difficulty="medium", co="CO2", bl="understand", kc="conceptual", pi="PI2.1"),
            dict(text="Apply bubble sort on [64,34,25,12,22,11,90] and trace all passes.", subject="Data Structures", unit="Unit 3", marks=6, difficulty="medium", co="CO3", bl="apply", kc="procedural", pi="PI2.2"),
            dict(text="Design and implement a hash table with chaining collision resolution.", subject="Data Structures", unit="Unit 5", marks=10, difficulty="hard", co="CO5", bl="create", kc="procedural", pi="PI3.1"),
            dict(text="Construct an AVL tree by inserting keys: 30,20,10,25,40,50,35. Show all rotations.", subject="Data Structures", unit="Unit 4", marks=10, difficulty="hard", co="CO5", bl="create", kc="procedural", pi="PI3.1"),
        ],
        'arts_science': [
            dict(text="Define an algorithm and state its characteristics.", subject="Computer Science", unit="Unit 1", marks=2, difficulty="easy", co="CO1", po="PO1", pso="PSO1"),
            dict(text="List any four applications of computers in daily life.", subject="Computer Science", unit="Unit 1", marks=2, difficulty="easy", co="CO1", po="PO1", pso="PSO1"),
            dict(text="Explain the von Neumann architecture with a block diagram.", subject="Computer Science", unit="Unit 2", marks=5, difficulty="medium", co="CO2", po="PO2", pso="PSO1"),
            dict(text="Describe cloud computing and explain IaaS, PaaS, SaaS.", subject="Computer Science", unit="Unit 5", marks=5, difficulty="medium", co="CO3", po="PO4", pso="PSO3"),
            dict(text="Analyse the impact of artificial intelligence on society.", subject="Computer Science", unit="Unit 5", marks=10, difficulty="hard", co="CO5", po="PO5", pso="PSO3"),
        ],
        'school': [
            dict(text="Define chemical reaction. Give one example.", subject="Science", unit="Chapter 1", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Chemical Reactions"),
            dict(text="State Newton's first law of motion.", subject="Science", unit="Chapter 9", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Force and Laws"),
            dict(text="Explain the types of chemical reactions with balanced equations.", subject="Science", unit="Chapter 1", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Chemical Reactions"),
            dict(text="Describe photosynthesis and write the overall equation.", subject="Science", unit="Chapter 6", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Life Processes"),
            dict(text="Evaluate the impact of deforestation on biodiversity.", subject="Science", unit="Chapter 15", marks=5, difficulty="hard", learning_outcome="LO5", chapter="Our Environment"),
        ],
    }
    seeded = 0
    for inst_type, questions in QUESTIONS.items():
        docs = []
        for q in questions:
            doc = dict(q)
            doc['institution_type'] = inst_type
            doc['created_by']       = 'seed'
            doc['created_at']       = datetime.utcnow()
            for field in ['co','bl','kc','pi','po','pso','chapter','learning_outcome']:
                doc.setdefault(field, '')
            docs.append(doc)
        mongo.db.questions.insert_many(docs)
        seeded += len(docs)
        print(f"[SEED] ✓ {inst_type}: {len(docs)} questions")
    print(f"[SEED] ✓ Total: {seeded} questions seeded")


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)