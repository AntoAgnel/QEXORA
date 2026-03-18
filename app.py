import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, session
from datetime import timedelta
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# Create extensions without app
mongo         = PyMongo()
bcrypt        = Bcrypt()
login_manager = LoginManager()
mail          = Mail()

def create_app():
    app = Flask(__name__)

    # Get URI from environment
    MONGO_URI = os.environ.get('MONGO_URI', '')
    print(f"[STARTUP] MONGO_URI loaded: {'YES' if MONGO_URI else 'NO'}")
    print(f"[STARTUP] URI preview: {MONGO_URI[:50] if MONGO_URI else 'EMPTY'}")

    # Set all config directly
    app.config['SECRET_KEY']          = os.environ.get('SECRET_KEY', 'qexora-fallback-key')
    app.config['MONGO_URI']           = MONGO_URI
    app.config['DEBUG']               = False
    app.config['MAIL_SERVER']         = 'smtp.gmail.com'
    app.config['MAIL_PORT']           = 587
    app.config['MAIL_USE_TLS']        = True
    app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_APP_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')
    app.permanent_session_lifetime    = timedelta(seconds=1800)

    # Initialize extensions with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view             = 'auth.login'
    login_manager.login_message_category = 'info'

    # Test connection on startup
    with app.app_context():
        try:
            mongo.db.list_collection_names()
            print("[STARTUP] ✓ MongoDB connected successfully")
        except Exception as e:
            print(f"[STARTUP] ✗ MongoDB connection failed: {e}")

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

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)