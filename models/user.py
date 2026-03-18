from flask_login import UserMixin
from bson import ObjectId
from datetime import datetime, timedelta
import random, string
from extensions import mongo, bcrypt

SUPERADMIN_EMAIL = "antoagnel289"

def is_superadmin(email):
    return email and email.lower().startswith("antoagnel289")

class User(UserMixin):
    def __init__(self, user_doc):
        self.id               = str(user_doc['_id'])
        self.name             = user_doc.get('name', '')
        self.email            = user_doc.get('email', '')
        self.role             = user_doc.get('role', 'faculty')
        self.institution_type = user_doc.get('institution_type', 'engineering')
        self.avatar           = user_doc.get('avatar', '')
        self.google_id        = user_doc.get('google_id', '')
        self.phone            = user_doc.get('phone', '')
        self.department       = user_doc.get('department', '')
        self.bio              = user_doc.get('bio', '')

    @property
    def is_superadmin(self):
        return is_superadmin(self.email)

    @property
    def is_admin(self):
        return self.role in ('admin', 'superadmin') or self.is_superadmin

    @property
    def initials(self):
        parts = self.name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return self.name[:2].upper() if self.name else 'U'

    @staticmethod
    def create(name, email, password=None, role='faculty',
               institution_type='engineering', google_id=''):
        if is_superadmin(email):
            role = 'superadmin'
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8') if password else ''
        doc = {
            'name': name, 'email': email,
            'password': hashed_pw, 'role': role,
            'institution_type': institution_type,
            'google_id': google_id,
            'phone': '', 'department': '', 'bio': '', 'avatar': '',
            'created_at': datetime.utcnow()
        }
        result = mongo.db.users.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def find_by_google_id(google_id):
        return mongo.db.users.find_one({'google_id': google_id})

    @staticmethod
    def check_password(hashed_pw, password):
        if not hashed_pw:
            return False
        return bcrypt.check_password_hash(hashed_pw, password)

    @staticmethod
    def update_password(user_id, new_password):
        hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
        mongo.db.users.update_one({'_id': ObjectId(user_id)},
                                  {'$set': {'password': hashed}})

    @staticmethod
    def update_profile(user_id, data):
        allowed = ['name', 'phone', 'department', 'bio', 'avatar']
        update  = {k: v for k, v in data.items() if k in allowed}
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update})

    @staticmethod
    def update_role(user_id, role):
        mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'role': role}})

    @staticmethod
    def update_institution(user_id, institution_type):
        mongo.db.users.update_one({'_id': ObjectId(user_id)},
                                  {'$set': {'institution_type': institution_type}})

    @staticmethod
    def delete(user_id):
        mongo.db.users.delete_one({'_id': ObjectId(user_id)})

    @staticmethod
    def get_all():
        return list(mongo.db.users.find().sort('created_at', -1))

    @staticmethod
    def count():
        return mongo.db.users.count_documents({})

    # ── OTP methods ──────────────────────────────────────────────────────────
    @staticmethod
    def set_otp(email):
        """Generate a 6-digit OTP valid for 10 minutes."""
        otp     = ''.join(random.choices(string.digits, k=6))
        expires = datetime.utcnow() + timedelta(minutes=10)
        mongo.db.users.update_one(
            {'email': email},
            {'$set': {'otp': otp, 'otp_expires': expires}}
        )
        return otp

    @staticmethod
    def verify_otp(email, otp):
        user = mongo.db.users.find_one({'email': email})
        if not user:
            return False, 'Email not found.'
        if user.get('otp') != otp:
            return False, 'Incorrect OTP.'
        if datetime.utcnow() > user.get('otp_expires', datetime.utcnow()):
            return False, 'OTP has expired. Please request a new one.'
        # Clear OTP after successful verification
        mongo.db.users.update_one({'email': email},
                                  {'$unset': {'otp': '', 'otp_expires': ''}})
        return True, 'OTP verified.'
