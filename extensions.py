from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

bcrypt        = Bcrypt()
login_manager = LoginManager()
mail          = Mail()

class MongoDB:
    def __init__(self):
        self._client = None
        self._db     = None

    def init_app(self, app):
        uri = app.config.get('MONGO_URI', '')
        print(f"[MongoDB] Connecting to: {uri[:50]}")
        try:
            self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            db_name      = uri.split('/')[-1].split('?')[0] or 'qexora_db'
            self._db     = self._client[db_name]
            # Test connection
            self._client.admin.command('ping')
            print(f"[MongoDB] ✓ Connected to database: {db_name}")
        except Exception as e:
            print(f"[MongoDB] ✗ Connection failed: {e}")

    @property
    def db(self):
        return self._db

mongo = MongoDB()