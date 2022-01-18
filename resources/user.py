import sqlite3
import datetime
import tinify
import os

from firebase_admin import auth
from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.datastructures import FileStorage
from flask_jwt_extended import (
                        create_access_token,
                        create_refresh_token,
                        get_jwt_identity,
                        jwt_refresh_token_required,
                        jwt_required)
from sqlalchemy_imageattach.context import store_context
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore

fs_store = HttpExposedFileSystemStore(
    '/var/www/html/items-rest/images',
    'images/',
    host_url_getter=lambda:'https://{0}/'.format(app.config['SERVER_NAME'])
)


class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('token', type=str, required=True, help='Token is required')
    parser.add_argument('user_name', type=str)
    parser.add_argument('platform', type=str)

    def post(self):
        data = UserRegister.parser.parse_args()
        try:
            decoded_token = auth.verify_id_token(data['token'])
            uid = decoded_token['uid']
            
            expires = datetime.timedelta(days=90)
            access_token = create_access_token(identity=uid, expires_delta=expires)
            refresh_token = create_refresh_token(identity=uid)

            user = UserModel.find_by_firebase_uid(uid)

            if user:
                return {
                'user': user.json(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

            photo_url = decoded_token.get('picture')
            firebase_user = auth.get_user(uid)

            if firebase_user.display_name:
                userName = firebase_user.display_name
            elif data['user_name']:
                userName = data['user_name']
            else:
                userName = "User"

            platform = data['platform']

            user = UserModel(userName, uid, photo_url, data['platform'])
            user.save_to_db()
        except auth.RevokedIdTokenError as ex:
            return {"error": 'ID token has been revoked'}
        except auth.ExpiredIdTokenError as ex:
            return {"error": 'ID token is expired'}
        except auth.InvalidIdTokenError as ex:
           return {"error": 'ID token is invalid'}
        except AssertionError as error:
            return {'message': 'firebase authentication failed', 'error': error}, 500

        return {
            'user': user.json(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200


class UserEdit(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str)
    parser.add_argument('avatar', type=FileStorage, location='files')

    @jwt_required
    def patch(self):
        data = UserEdit.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)
        new_name = data['name']
        new_avatar = data['avatar']

        if new_name:
            user.username = new_name
        
        if new_avatar:
            tinify.key = '6hkCL3CKB7dXjqtttq112fkK5Hf63t5x'
            compressed_avatar = tinify.from_file(new_avatar)
            compressed_avatar.to_file("var/www/html/items-rest/compressed/" + new_avatar.filename)

            with store_context(fs_store):
                with open("var/www/html/items-rest/compressed/" + new_avatar.filename, 'rb') as f:
                    user.avatar.from_file(f)

        try:
            user.save_to_db()
            return {
                'message': 'user is edited successfully',
                'user': user.json()
            }
        except:
            return {"error": "cannot save edited user"}, 500


class UserList(Resource):
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}


class UserRefresh(Resource):
    @jwt_refresh_token_required
    def get(self):
        current_user = get_jwt_identity()
        expires = datetime.timedelta(days=1)

        new_token = create_access_token(identity=current_user, expires_delta=expires)
        return {'access_token': new_token}, 200
