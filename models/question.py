from bson import ObjectId
from datetime import datetime
from extensions import mongo

class Question:
    """
    Represents a question in the centralized question bank.
    Supports multiple institution types with dynamic mapping fields.
    """

    @staticmethod
    def create(data):
        """
        data keys:
          text, subject, unit, marks, difficulty,
          institution_type,
          # Engineering
          co, bl, kc, pi,
          # Arts & Science
          po, pso,
          # School
          chapter, learning_outcome,
          created_by (user_id)
        """
        doc = {
            'text':             data.get('text', ''),
            'subject':          data.get('subject', ''),
            'unit':             data.get('unit', ''),
            'marks':            int(data.get('marks', 2)),
            'difficulty':       data.get('difficulty', 'medium'),   # easy | medium | hard
            'institution_type': data.get('institution_type', 'engineering'),
            # Engineering mappings
            'co':               data.get('co', ''),
            'bl':               data.get('bl', ''),
            'kc':               data.get('kc', ''),
            'pi':               data.get('pi', ''),
            # Arts & Science mappings
            'po':               data.get('po', ''),
            'pso':              data.get('pso', ''),
            # School mappings
            'chapter':          data.get('chapter', ''),
            'learning_outcome': data.get('learning_outcome', ''),
            'created_by':       data.get('created_by', ''),
            'created_at':       datetime.utcnow()
        }
        result = mongo.db.questions.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_all(institution_type=None, filters=None):
        query = {}
        if institution_type:
            query['institution_type'] = institution_type
        if filters:
            query.update(filters)
        return list(mongo.db.questions.find(query))

    @staticmethod
    def get_by_id(question_id):
        return mongo.db.questions.find_one({'_id': ObjectId(question_id)})

    @staticmethod
    def update(question_id, data):
        mongo.db.questions.update_one(
            {'_id': ObjectId(question_id)},
            {'$set': data}
        )

    @staticmethod
    def delete(question_id):
        mongo.db.questions.delete_one({'_id': ObjectId(question_id)})

    @staticmethod
    def count(filters=None):
        return mongo.db.questions.count_documents(filters or {})
