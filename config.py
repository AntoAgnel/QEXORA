import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY  = os.environ.get('SECRET_KEY', 'qexora-secret-key-change-in-production')
    MONGO_URI   = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/qexora_db')
    DEBUG       = os.environ.get('DEBUG', 'True') == 'True'

    # Session timeout – 30 minutes of inactivity
    PERMANENT_SESSION_LIFETIME = 1800   # seconds
    SESSION_COOKIE_HTTPONLY     = True
    SESSION_COOKIE_SAMESITE     = 'Lax'

    # Flask-Mail (Gmail SMTP)
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_APP_PASSWORD', '')   # Gmail App Password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', '')

    # Google OAuth
    GOOGLE_CLIENT_ID     = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

    # AI
    GROQ_API_KEY   = os.environ.get('GROQ_API_KEY', '')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
