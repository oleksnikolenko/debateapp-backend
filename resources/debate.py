import tinify

from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from models.debate import DebateModel
from models.side import SideModel
from models.user import UserModel
from models.category import CategoryModel
from werkzeug.datastructures import FileStorage
from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from sqlalchemy_imageattach.context import store_context
from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AAAAPZu__aA:APA91bGoAzc28Omj4zsSHI4p2GujaykOuKP4zbXDkc0P8UIKPkXvSahhv7QNbgO-nhu9ev4_kYjwlEsiPucmXR0y7cTUrN0BMzI61Snf6lzudR7Gkz0ki6zMCvLvjs7pliDKSLj_RQ7p")


fs_store = HttpExposedFileSystemStore(
    '/var/www/html/debates-rest/debates-rest-api-production/images',
    'images/',
    host_url_getter=lambda:'https://{0}/'.format(app.config['SERVER_NAME'])
)

class Debate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('debate_id', type=str, required=True, help="debate_id is needed")
    parser.add_argument('user_id', type=str, required=False)

    # New debate image (statement type)
    parser.add_argument('new_image', type=FileStorage, location='files')

    @jwt_optional
    def get(self):
        # registration_id = "c19r71kBVUFUmFFkwe8Sap:APA91bF46uQbIspjblUtESvu2NqzZujFVYAUD3psMAQxjnaC4Tfn-bEo8EX3N7kOuDUg6QNGYtOK6xTDFmxtN21XTedcOgXc9AtCutyE8fDke8aP1IyslC9lDw2mVq-9behz_ls3iJKU"
        # message_title = "Hi buddy"
        # message_body = "This is real push, yay"
        # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

        data = Debate.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)
        user_id = user.id if user else None

        debate = DebateModel.find_by_id(data['debate_id'])
        if debate:
            return debate.json(user_id)
        return {'message': 'Debate not found'}, 400

    def delete(self):
        data = Debate.parser.parse_args()

        debate = DebateModel.find_by_id(data['debate_id'])
        if debate:
            debate.delete_from_db()
            return {'message': 'Debate deleted'}, 200
        else:
            return {'message': 'Debate not found'}, 400
    
    @jwt_required
    def patch(self):
        data = Debate.parser.parse_args()

        new_image = data['new_image']
        debate = DebateModel.find_by_id(data['debate_id'])

        if debate:
            if new_image:
                with store_context(fs_store):
                    debate.image.from_file(new_image)
        else:
            return {"error": "debate not found"}, 400

        try:
            debate.save_to_db()
            return {
                'message': 'debate is edited successfully',
                'user': debate.json()
            }
        except:
            return {"error": "cannot save edited debate"}, 500


class DebateList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int)
    parser.add_argument('category_id', type=str)
    parser.add_argument('sorting', type=str)

    @jwt_optional
    def get(self, localization):
        data = DebateList.parser.parse_args()
        page = data['page']

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)
        user_id = user.id if user else None

        per_page = 10

        category_id = data['category_id']
        sorting = data['sorting']

        categories = CategoryModel.filter_by_localization(localization)
        categories_list = [category.json() for category in categories]

        if category_id: #and category_id != 'all':
            if category_id == 'favorites':
                from models.favoritedebate import FavoriteDebateModel
                if user:
                    localized_debates = FavoriteDebateModel.filter_by_user_id(user.id, sorting)
                else:
                    return {
                        'debates': [],
                        'has_next_page': False,
                        'categories': categories_list
                    }
            elif category_id != 'all':
                localized_debates = DebateModel.filter_by_category_and_localization(category_id, localization, sorting)
            else:
                localized_debates = DebateModel.filter_by_localization(localization, sorting)
        else:
            localized_debates = DebateModel.filter_by_localization(localization, sorting)

        has_next_page = localized_debates.paginate(page if page else 1, per_page, error_out=False).has_next
        debates_list = [debate.json(user_id) for debate in localized_debates.paginate(page, per_page, error_out=False).items]

        return {
            'debates': debates_list,
            'has_next_page': has_next_page,
            'categories': categories_list
        }

class DebateCreator(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('category_list', type=str, action='append', required=True, help="category_list is missing")
    parser.add_argument('leftside_name', type=str, required=True, help="leftside_name is missing")
    parser.add_argument('leftside_image', type=FileStorage, location='files')
    parser.add_argument('rightside_name', type=str, required=True, help="rightside_name is missing")
    parser.add_argument('rightside_image', type=FileStorage, location='files')
    parser.add_argument('name', type=str)
    parser.add_argument('debate_type', type=str)
    parser.add_argument('debate_image', type=FileStorage, location='files')

    @jwt_required
    def post(self, localization):
        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        if user.is_banned:
            return {"message": "user is banned"}, 403
        data = DebateCreator.parser.parse_args()

        tinify.key = '6hkCL3CKB7dXjqtttq112fkK5Hf63t5x'

        leftside = SideModel(data['leftside_name'])
        rightside = SideModel(data['rightside_name'])

        left_image = data['leftside_image']
        right_image = data['rightside_image']
        debate_type = data['debate_type']
        debate_image = data['debate_image']

        if debate_type == "sides":
            compressed_left_image = tinify.from_file(left_image).to_file("var/www/html/debates-rest/debates-rest-api-production/compressed/" + left_image.filename)
            compressed_right_image = tinify.from_file(right_image).to_file("var/www/html/debates-rest/debates-rest-api-production/compressed/" + right_image.filename)

            with store_context(fs_store):
                 with open("var/www/html/debates-rest/debates-rest-api-production/compressed/" + left_image.filename, 'rb') as f:
                    leftside.image.from_file(f)

            with store_context(fs_store):
                 with open("var/www/html/debates-rest/debates-rest-api-production/compressed/" + right_image.filename, 'rb') as f:
                    rightside.image.from_file(f)

        try:
            leftside.save_to_db()
        except AssertionError as error:
            return {"message": "Error while saving leftSide", "error": error}, 500

        try:
            rightside.save_to_db()
        except AssertionError as error:
            return {"message": "Error while saving rightside", "error": error}, 500

        debate = DebateModel(data['name'], leftside.id, rightside.id, data['category_list'], localization, user.id, data['debate_type'])

        if debate_type == "statement":
            compressed_image = tinify.from_file(debate_image).to_file("var/www/html/debates-rest/debates-rest-api-production/compressed/" + debate_image.filename)

            with store_context(fs_store):
                with open("var/www/html/debates-rest/debates-rest-api-production/compressed/" + debate_image.filename, 'rb') as f:
                    debate.image.from_file(f)

        try:
            debate.save_to_db()
        except AssertionError as error:
            return {'message': 'Error while saving debate', 'error': error}, 500

        return debate.json(None), 201