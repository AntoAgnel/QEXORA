from flask import current_app
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# These are accessed via current_app.mongo etc.
# Kept here for compatibility with models that import from extensions
def get_mongo():
    return current_app.mongo

class _MongoProxy:
    @property
    def db(self):
        return current_app.mongo.db
    def init_app(self, app):
        pass

class _BcryptProxy:
    def generate_password_hash(self, pw):
        return current_app.bcrypt.generate_password_hash(pw)
    def check_password_hash(self, h, pw):
        return current_app.bcrypt.check_password_hash(h, pw)
    def init_app(self, app):
        pass

class _MailProxy:
    def send(self, msg):
        return current_app.mail.send(msg)
    def init_app(self, app):
        pass

class _LoginProxy:
    def init_app(self, app):
        pass

mongo         = _MongoProxy()
bcrypt        = _BcryptProxy()
login_manager = _LoginProxy()
mail          = _MailProxy()