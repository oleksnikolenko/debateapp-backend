from flask_restful import Resource,reqparse
from models.userfeedback import UserFeedbackModel

class UserFeedback(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('key', type=str, required=True, help="Key is missing")
    parser.add_argument('text', type=str, required=True, help="Text is missing")

    def post(self):
        data = UserFeedback.parser.parse_args()

        userfeedback = UserFeedbackModel(data['key'], data['text'])

        try:
            userfeedback.save_to_db()
        except AssertionError as error:
            return {'error': error}, 500
        
        return {'message': 'success'}, 201