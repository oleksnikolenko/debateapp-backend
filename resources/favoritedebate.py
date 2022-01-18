from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.favoritedebate import FavoriteDebateModel
from models.user import UserModel
from models.debate import DebateModel


class FavoriteDebate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('debate_id', type=str)
    parser.add_argument('page', type=int)

    @jwt_required
    def get(self):
        data = FavoriteDebate.parser.parse_args()
        page = data['page']

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        per_page = 10

        favorite_debates = FavoriteDebateModel.filter_by_user_id(user.id)

        has_next_page = favorite_debates.paginate(page if page else 1, per_page, error_out=False).has_next
        debates_list = [debate.json(user.id) for debate in favorite_debates.paginate(page, per_page, error_out=False).items]

        return {
            'debates': debates_list,
            'has_next_page': has_next_page
        }

    @jwt_required
    def post(self):
        data = FavoriteDebate.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        favorite_debate = FavoriteDebateModel(data['debate_id'], user.id)
        favorite_debate.save_to_db()

        return {'message': 'successfully added favorites'}, 201

    @jwt_required
    def delete(self):
        data = FavoriteDebate.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        favorite_debate = FavoriteDebateModel.find_by_user_and_debate(user.id, data['debate_id'])
        favorite_debate.delete_from_db()

        return {'message': 'successfully deleted favorites'}