from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_optional, get_jwt_identity
from models.user import UserModel
from models.device import DeviceModel


class Device(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('device_id', type=str, required=True, help="device_id is needed")
    parser.add_argument('push_token', type=str, required=True, help="push_token is needed")
    parser.add_argument('localization', type=str, required=True, help="localization is needed")

    @jwt_optional
    def post(self):
        data = Device.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        device = DeviceModel.find_by_device_id(data['device_id'])

        if not device:
            device = DeviceModel(data['device_id'], data['push_token'], data['localization'])
            device.save_to_db()
            return {'message': 'succesfully created a new device'}, 201

        if user:
            device.user_id = user.id
            device.push_token = data['push_token']
            device.localization_name = data['localization']

            device.save_to_db()
            return {'message': 'successfully matched user and device'}, 200
        else:
            device.push_token = data['push_token']
            device.localization_name = data['localization']

            device.save_to_db()
            return {'message': 'succesfully updated device, but without user'}, 200
