from bson import ObjectId
from datetime import datetime
from extensions import mongo

class QuestionPaper:
    @staticmethod
    def create(data):
        doc = {
            'title':            data.get('title', ''),
            'subject':          data.get('subject', ''),
            'institution_type': data.get('institution_type', ''),
            'template_id':      data.get('template_id', ''),
            'sections':         data.get('sections', []),   # list of {section_name, questions:[]}
            'total_marks':      data.get('total_marks', 0),
            'analytics':        data.get('analytics', {}), # CO coverage, BL distribution, etc.
            'created_by':       data.get('created_by', ''),
            'created_at':       datetime.utcnow()
        }
        result = mongo.db.question_papers.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_all(created_by=None):
        query = {}
        if created_by:
            query['created_by'] = created_by
        return list(mongo.db.question_papers.find(query).sort('created_at', -1))

    @staticmethod
    def get_by_id(paper_id):
        return mongo.db.question_papers.find_one({'_id': ObjectId(paper_id)})

    @staticmethod
    def delete(paper_id):
        mongo.db.question_papers.delete_one({'_id': ObjectId(paper_id)})
