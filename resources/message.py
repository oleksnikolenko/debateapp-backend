import datetime

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional
from models.message import MessageModel
from models.reply import ReplyModel
from models.user import UserModel
from pyfcm import FCMNotification


class Message(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('text', type=str)
    parser.add_argument('debate_id', type=str)
    parser.add_argument('message_id', type=str)
    parser.add_argument('thread_id', type=str)

    @jwt_required
    def post(self):
        data = Message.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        thread_id = data['thread_id']

        if thread_id:
            reply = ReplyModel(data['text'], user.id, thread_id)
            reply.save_to_db()
            return reply.json(user.id), 201
        else:
            message = MessageModel(data['text'], user.id, data['debate_id'])
            return self.post_message(message)

    @jwt_required
    def delete(self):
        data = Message.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        thread_id = data['thread_id']

        if thread_id:
            message = ReplyModel.find_by_id(data['message_id'])
        else:
            message = MessageModel.find_by_id(data['message_id'])
        return self.delete_message(message, user.id)

    @jwt_required
    def patch(self):
        data = Message.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        thread_id = data['thread_id']

        if thread_id:
            message = ReplyModel.find_by_id(data['message_id'])
        else:
            message = MessageModel.find_by_id(data['message_id'])
        return self.patch_message(message, data['text'], user.id)

    def post_message(self, message):
        try:
            message.save_to_db()
        except:
            return {"message": "An error occured saving message"}, 500

        return message.json(None), 201

    def delete_message(self, message, user_id):
        if message:
            if message.user_id == user_id:
                message.delete_from_db()
                return {'success': True}, 200
            else:
                return {'error': "This user is not allowed to delete this message"}, 401
        else:
            return {"error": "Message is not found"}, 400

    def patch_message(self, message, text, user_id):
        if message:
            if message.user_id == user_id:
                message.text = text
                message.edited_date = datetime.datetime.utcnow()
                message.is_edited = True
                # try:
                message.save_to_db()
                return message.json(user_id), 200
                # except:
                #     return {"error": "Error while saving message to db"}, 500
            else:
                return {'error': "This user is not allowed to edit this message"}, 401
        else:
            return {"error": "Message is not found"}, 400


class MessageList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('debate_id', type=str)
    parser.add_argument('thread_id', type=str)
    parser.add_argument('after_time', type=float)

    @jwt_optional
    def get(self):
        data = MessageList.parser.parse_args()

        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)
        user_id = user.id if user else None

        thread_id = data['thread_id']

        if thread_id:
            messages = ReplyModel.find_after_time(data['thread_id'], data['after_time'])
            message_list = [message.json(user_id) for message in messages.paginate(1, 5, error_out=False).items]
            message_list.reverse()
            return {
                'messages': message_list,
                'has_next_page': messages.paginate(1, 10, error_out=False).has_next
            }, 200
        else:
            messages = MessageModel.find_after_time(data['debate_id'], data['after_time'])
            return {
                'messages': [message.json(user_id) for message in messages.paginate(1, 10, error_out=False).items],
                'has_next_page': messages.paginate(1, 10, error_out=False).has_next
            }, 200
