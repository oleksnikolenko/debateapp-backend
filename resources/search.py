from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_optional, get_jwt_identity
from models.side import SideModel
from models.user import UserModel
from models.debate import DebateModel

class Search(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('search_context', type=str, required=True, help='search_context is required')
    parser.add_argument('page', type=int)

    @jwt_optional
    def get(self, localization):
        data = Search.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)
        user_id = user.id if user else None

        per_page = 10
        page = data['page']

        debates = DebateModel.filter_by_context_and_localization(data['search_context'], localization)

        if debates:
            debates_list = [debate.json(user_id) for debate in debates.paginate(page if page else 1, per_page, error_out=False).items]
            has_next_page = debates.paginate(page if page else 1, per_page, error_out=False).has_next

            return {
                'debates': debates_list,
                'has_next_page': has_next_page
            }
        else:
            return {
                'debates': [],
                'has_next_page': False,
                'message': 'context not found'
            }