from flask import Flask, session, redirect, url_for, request
from datetime import timedelta
from config import Config
from extensions import mongo, bcrypt, login_manager, mail
from routes.auth     import auth_bp
from routes.dashboard import dashboard_bp
from routes.questions import questions_bp
from routes.mapping   import mapping_bp
from routes.paper_templates import templates_bp
from routes.generation import generation_bp
from routes.analytics  import analytics_bp
from routes.dev        import dev_bp
from routes.settings   import settings_bp
from routes.editor     import editor_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Permanent session with timeout
    app.permanent_session_lifetime = timedelta(seconds=config_class.PERMANENT_SESSION_LIFETIME)

    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view         = 'auth.login'
    login_manager.login_message      = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @app.before_request
    def make_session_permanent():
        session.permanent = True

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
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
