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

    print("[STARTUP] ✓ App created successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)