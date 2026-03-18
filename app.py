import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, session
from datetime import timedelta

def create_app():
    app = Flask(__name__)

    MONGO_URI = os.environ.get('MONGO_URI', '')
    print(f"[STARTUP] MONGO_URI: {'YES - ' + MONGO_URI[:40] if MONGO_URI else 'EMPTY!'}")

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

    from flask_pymongo import PyMongo
    from flask_bcrypt import Bcrypt
    from flask_login import LoginManager
    from flask_mail import Mail

    mongo         = PyMongo(app)
    bcrypt        = Bcrypt(app)
    login_manager = LoginManager(app)
    mail          = Mail(app)

    login_manager.login_view             = 'auth.login'
    login_manager.login_message_category = 'info'

    # Store on app so extensions.py can access them
    app.mongo         = mongo
    app.bcrypt        = bcrypt
    app.login_manager = login_manager
    app.mail          = mail

    # Register user_loader
    from bson import ObjectId
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        try:
            user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            return User(user) if user else None
        except Exception:
            return None

    @app.before_request
    def make_session_permanent():
        session.permanent = True

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

    # Auto-seed database on startup if empty
    with app.app_context():
        try:
            from models.paper_template import PaperTemplate
            from datetime import datetime

            # Seed templates
            PaperTemplate.seed_defaults()

            # Seed questions if empty
            total = mongo.db.questions.count_documents({})
            if total == 0:
                print("[SEED] No questions found — seeding now...")

                QUESTIONS = {
                    'engineering': [
                        dict(text="Define data structure and list its types.", subject="Data Structures", unit="Unit 1", marks=2, difficulty="easy", co="CO1", bl="remember", kc="factual", pi="PI1.1"),
                        dict(text="State the LIFO principle used in stack operations.", subject="Data Structures", unit="Unit 1", marks=2, difficulty="easy", co="CO1", bl="remember", kc="factual", pi="PI1.1"),
                        dict(text="List the differences between stack and queue.", subject="Data Structures", unit="Unit 1", marks=2, difficulty="easy", co="CO1", bl="remember", kc="conceptual", pi="PI1.2"),
                        dict(text="Define sorting. Name any two comparison-based sorting algorithms.", subject="Data Structures", unit="Unit 3", marks=2, difficulty="easy", co="CO1", bl="remember", kc="factual", pi="PI1.1"),
                        dict(text="State the Big-O time complexity of linear search.", subject="Data Structures", unit="Unit 3", marks=2, difficulty="easy", co="CO2", bl="remember", kc="factual", pi="PI1.2"),
                        dict(text="Explain the working of a circular queue with a suitable example.", subject="Data Structures", unit="Unit 1", marks=6, difficulty="medium", co="CO2", bl="understand", kc="conceptual", pi="PI2.1"),
                        dict(text="Apply bubble sort on the array [64,34,25,12,22,11,90] and trace all passes.", subject="Data Structures", unit="Unit 3", marks=6, difficulty="medium", co="CO3", bl="apply", kc="procedural", pi="PI2.2"),
                        dict(text="Explain binary search tree insertion with a step-by-step example.", subject="Data Structures", unit="Unit 4", marks=6, difficulty="medium", co="CO3", bl="understand", kc="conceptual", pi="PI2.1"),
                        dict(text="Describe inorder, preorder, and postorder traversal of a binary tree.", subject="Data Structures", unit="Unit 4", marks=6, difficulty="medium", co="CO3", bl="understand", kc="conceptual", pi="PI2.1"),
                        dict(text="Solve the Tower of Hanoi problem for n=3 using recursion and trace all moves.", subject="Data Structures", unit="Unit 2", marks=6, difficulty="medium", co="CO3", bl="apply", kc="procedural", pi="PI2.2"),
                        dict(text="Design and implement a hash table with chaining collision resolution. Analyse average and worst-case time complexity.", subject="Data Structures", unit="Unit 5", marks=10, difficulty="hard", co="CO5", bl="create", kc="procedural", pi="PI3.1"),
                        dict(text="Compare and analyse the performance of merge sort and quick sort.", subject="Data Structures", unit="Unit 3", marks=10, difficulty="hard", co="CO4", bl="analyse", kc="metacognitive", pi="PI3.2"),
                        dict(text="Construct an AVL tree by inserting keys: 30, 20, 10, 25, 40, 50, 35. Show all rotations.", subject="Data Structures", unit="Unit 4", marks=10, difficulty="hard", co="CO5", bl="create", kc="procedural", pi="PI3.1"),
                        dict(text="Develop a graph representation and implement BFS and DFS traversal on a 6-node graph.", subject="Data Structures", unit="Unit 5", marks=10, difficulty="hard", co="CO5", bl="create", kc="procedural", pi="PI3.2"),
                        dict(text="Evaluate the time and space complexity of Quicksort, Mergesort, and Heapsort.", subject="Data Structures", unit="Unit 3", marks=10, difficulty="hard", co="CO4", bl="evaluate", kc="metacognitive", pi="PI3.1"),
                    ],
                    'arts_science': [
                        dict(text="Define an algorithm and state its characteristics.", subject="Introduction to Computer Science", unit="Unit 1", marks=2, difficulty="easy", co="CO1", po="PO1", pso="PSO1"),
                        dict(text="List any four applications of computers in daily life.", subject="Introduction to Computer Science", unit="Unit 1", marks=2, difficulty="easy", co="CO1", po="PO1", pso="PSO1"),
                        dict(text="Define primary memory and secondary memory with examples.", subject="Introduction to Computer Science", unit="Unit 2", marks=2, difficulty="easy", co="CO1", po="PO1", pso="PSO1"),
                        dict(text="State the difference between hardware and software.", subject="Introduction to Computer Science", unit="Unit 2", marks=2, difficulty="easy", co="CO1", po="PO1", pso="PSO1"),
                        dict(text="Identify the function of an operating system.", subject="Introduction to Computer Science", unit="Unit 3", marks=2, difficulty="easy", co="CO2", po="PO2", pso="PSO2"),
                        dict(text="Explain the von Neumann architecture of a computer with a block diagram.", subject="Introduction to Computer Science", unit="Unit 2", marks=5, difficulty="medium", co="CO2", po="PO2", pso="PSO1"),
                        dict(text="Describe the functions of an operating system and explain any two types.", subject="Introduction to Computer Science", unit="Unit 3", marks=5, difficulty="medium", co="CO3", po="PO2", pso="PSO2"),
                        dict(text="Explain the differences between machine language, assembly language, and high-level language.", subject="Introduction to Computer Science", unit="Unit 4", marks=5, difficulty="medium", co="CO3", po="PO3", pso="PSO2"),
                        dict(text="Describe the client-server model with a suitable real-world example.", subject="Introduction to Computer Science", unit="Unit 5", marks=5, difficulty="medium", co="CO3", po="PO3", pso="PSO2"),
                        dict(text="Describe cloud computing and explain its service models: IaaS, PaaS, and SaaS.", subject="Introduction to Computer Science", unit="Unit 5", marks=5, difficulty="medium", co="CO3", po="PO4", pso="PSO3"),
                        dict(text="Analyse the impact of artificial intelligence on employment and society.", subject="Introduction to Computer Science", unit="Unit 5", marks=10, difficulty="hard", co="CO5", po="PO5", pso="PSO3"),
                        dict(text="Design an entity-relationship diagram for a library management system.", subject="Introduction to Computer Science", unit="Unit 3", marks=10, difficulty="hard", co="CO4", po="PO4", pso="PSO2"),
                        dict(text="Evaluate the trade-offs between CPU scheduling algorithms (FCFS, SJF, Round Robin).", subject="Introduction to Computer Science", unit="Unit 3", marks=10, difficulty="hard", co="CO5", po="PO4", pso="PSO3"),
                        dict(text="Compare relational and non-relational databases. Evaluate their suitability for a real-time social media application.", subject="Introduction to Computer Science", unit="Unit 3", marks=10, difficulty="hard", co="CO5", po="PO4", pso="PSO3"),
                        dict(text="Construct a truth table for a full adder circuit. Design the logic circuit using basic gates.", subject="Introduction to Computer Science", unit="Unit 1", marks=10, difficulty="hard", co="CO4", po="PO3", pso="PSO2"),
                    ],
                    'school': [
                        dict(text="Define chemical reaction. Give one example.", subject="Science", unit="Chapter 1", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Chemical Reactions and Equations"),
                        dict(text="State Newton's first law of motion.", subject="Science", unit="Chapter 9", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Force and Laws of Motion"),
                        dict(text="Name the process by which green plants prepare their own food.", subject="Science", unit="Chapter 6", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Life Processes"),
                        dict(text="Define an ecosystem and give one example.", subject="Science", unit="Chapter 15", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Our Environment"),
                        dict(text="State Ohm's Law.", subject="Science", unit="Chapter 12", marks=1, difficulty="easy", learning_outcome="LO1", chapter="Electricity"),
                        dict(text="Explain the types of chemical reactions with one balanced equation for each.", subject="Science", unit="Chapter 1", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Chemical Reactions and Equations"),
                        dict(text="Describe the process of photosynthesis and write the overall chemical equation.", subject="Science", unit="Chapter 6", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Life Processes"),
                        dict(text="Explain Newton's three laws of motion with real-life examples.", subject="Science", unit="Chapter 9", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Force and Laws of Motion"),
                        dict(text="Explain the refraction of light through a glass slab with a ray diagram.", subject="Science", unit="Chapter 11", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Light"),
                        dict(text="Describe the water cycle and its importance for maintaining life on Earth.", subject="Science", unit="Chapter 14", marks=3, difficulty="medium", learning_outcome="LO3", chapter="Sources of Energy"),
                        dict(text="Analyse the factors affecting rate of a chemical reaction. Design an experiment to demonstrate the effect of temperature.", subject="Science", unit="Chapter 1", marks=5, difficulty="hard", learning_outcome="LO5", chapter="Chemical Reactions and Equations"),
                        dict(text="Evaluate the impact of deforestation on biodiversity and climate change.", subject="Science", unit="Chapter 15", marks=5, difficulty="hard", learning_outcome="LO5", chapter="Our Environment"),
                        dict(text="A circuit has resistors 2 ohm, 4 ohm, and 6 ohm in parallel with 12V. Calculate total resistance and current.", subject="Science", unit="Chapter 12", marks=5, difficulty="hard", learning_outcome="LO5", chapter="Electricity"),
                        dict(text="Explain Mendel's laws and apply the law of segregation to predict offspring ratios.", subject="Science", unit="Chapter 9", marks=5, difficulty="hard", learning_outcome="LO5", chapter="Heredity and Evolution"),
                        dict(text="Evaluate Darwin's theory of natural selection. Discuss how it explains antibiotic resistance in bacteria.", subject="Science", unit="Chapter 9", marks=5, difficulty="hard", learning_outcome="LO5", chapter="Heredity and Evolution"),
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
                    print(f"[SEED] ✓ {inst_type}: {len(docs)} questions seeded")

                print(f"[SEED] ✓ Total seeded: {seeded} questions")
            else:
                print(f"[SEED] ✓ Database already has {total} questions — skipping seed")

        except Exception as e:
            print(f"[SEED] ✗ Seeding failed: {e}")

    print("[STARTUP] ✓ App ready")
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)