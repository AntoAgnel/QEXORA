from bson import ObjectId
from datetime import datetime
from extensions import mongo

class PaperTemplate:
    """
    Defines the structure of a question paper.
    Sections contain number of questions, marks per question, difficulty ratio.
    """

    @staticmethod
    def create(data):
        """
        data keys:
          name, institution_type, subject, total_marks,
          sections: [
            {
              section_name: 'Part A',
              question_type: 'short',
              num_questions: 10,
              marks_per_question: 2,
              difficulty_ratio: {easy: 0.5, medium: 0.3, hard: 0.2}
            }, ...
          ],
          created_by
        """
        doc = {
            'name':             data.get('name', ''),
            'institution_type': data.get('institution_type', 'engineering'),
            'subject':          data.get('subject', ''),
            'total_marks':      int(data.get('total_marks', 100)),
            'sections':         data.get('sections', []),
            'is_default':       data.get('is_default', False),
            'created_by':       data.get('created_by', ''),
            'created_at':       datetime.utcnow()
        }
        result = mongo.db.templates.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_all(institution_type=None):
        query = {}
        if institution_type:
            query['institution_type'] = institution_type
        return list(mongo.db.templates.find(query))

    @staticmethod
    def get_by_id(template_id):
        return mongo.db.templates.find_one({'_id': ObjectId(template_id)})

    @staticmethod
    def update(template_id, data):
        mongo.db.templates.update_one(
            {'_id': ObjectId(template_id)},
            {'$set': data}
        )

    @staticmethod
    def delete(template_id):
        mongo.db.templates.delete_one({'_id': ObjectId(template_id)})

    @staticmethod
    def seed_defaults():
        """Insert default ready-made templates if none exist."""
        if mongo.db.templates.count_documents({'is_default': True}) == 0:
            defaults = [
                {
                    'name': 'Engineering – Internal Assessment (50 Marks)',
                    'institution_type': 'engineering',
                    'subject': '',
                    'total_marks': 50,
                    'sections': [
                        {'section_name': 'Part A', 'question_type': 'short',
                         'num_questions': 10, 'marks_per_question': 2,
                         'difficulty_ratio': {'easy': 0.5, 'medium': 0.3, 'hard': 0.2}},
                        {'section_name': 'Part B', 'question_type': 'long',
                         'num_questions': 5, 'marks_per_question': 6,
                         'difficulty_ratio': {'easy': 0.2, 'medium': 0.5, 'hard': 0.3}}
                    ],
                    'is_default': True,
                    'created_by': 'system',
                    'created_at': datetime.utcnow()
                },
                {
                    'name': 'Arts & Science – Semester Exam (75 Marks)',
                    'institution_type': 'arts_science',
                    'subject': '',
                    'total_marks': 75,
                    'sections': [
                        {'section_name': 'Part A', 'question_type': 'short',
                         'num_questions': 10, 'marks_per_question': 2,
                         'difficulty_ratio': {'easy': 0.6, 'medium': 0.3, 'hard': 0.1}},
                        {'section_name': 'Part B', 'question_type': 'paragraph',
                         'num_questions': 5, 'marks_per_question': 5,
                         'difficulty_ratio': {'easy': 0.2, 'medium': 0.5, 'hard': 0.3}},
                        {'section_name': 'Part C', 'question_type': 'essay',
                         'num_questions': 3, 'marks_per_question': 10,
                         'difficulty_ratio': {'easy': 0.1, 'medium': 0.4, 'hard': 0.5}}
                    ],
                    'is_default': True,
                    'created_by': 'system',
                    'created_at': datetime.utcnow()
                },
                {
                    'name': 'School – Unit Test (25 Marks)',
                    'institution_type': 'school',
                    'subject': '',
                    'total_marks': 25,
                    'sections': [
                        {'section_name': 'Section A', 'question_type': 'mcq',
                         'num_questions': 5, 'marks_per_question': 1,
                         'difficulty_ratio': {'easy': 0.6, 'medium': 0.4, 'hard': 0.0}},
                        {'section_name': 'Section B', 'question_type': 'short',
                         'num_questions': 5, 'marks_per_question': 2,
                         'difficulty_ratio': {'easy': 0.4, 'medium': 0.4, 'hard': 0.2}},
                        {'section_name': 'Section C', 'question_type': 'long',
                         'num_questions': 2, 'marks_per_question': 5,
                         'difficulty_ratio': {'easy': 0.2, 'medium': 0.5, 'hard': 0.3}}
                    ],
                    'is_default': True,
                    'created_by': 'system',
                    'created_at': datetime.utcnow()
                }
            ]
            mongo.db.templates.insert_many(defaults)
