import datetime

from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional
from models.message import MessageModel
from models.reply import ReplyModel
from models.user import UserModel
from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AAAAPZu__aA:APA91bGoAzc28Omj4zsSHI4p2GujaykOuKP4zbXDkc0P8UIKPkXvSahhv7QNbgO-nhu9ev4_kYjwlEsiPucmXR0y7cTUrN0BMzI61Snf6lzudR7Gkz0ki6zMCvLvjs7pliDKSLj_RQ7p")


class Message(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('text', type=str)
    parser.add_argument('debate_id', type=str)
    parser.add_argument('message_id', type=str)
    parser.add_argument('thread_id', type=str)

    @jwt_required
    def post(self):
        data = Message.parser.parse_args()

########
        registration_id = "et_dYrsVf0FEni85bcyXjE:APA91bGxSZbz4jHEvCnZjsO4xcs1uGCbN7xx7xMDMhpW25kBOSrODAOpB17fLrv0WEa6D7nUL6fYrnDUIScQCz716Rfn_QAjY7F_YjrZkfRldq8tS5Gg_5JjatgKC6MFJMOX30gsUbgB"
        message_title = "Test push notification"
        message_body = "It works"
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
        print("CHECK")
########  
        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        thread_id = data['thread_id']

        if thread_id:
            reply = ReplyModel(data['text'], user.id, thread_id)
            # TODO: Find parent message and send push
            #parent_message = MessageModel.find_by_id(thread_id)
            #user_push_token = parent_message.user.push_token

            # {
            #     "to" : "dsjfsdlkfjdksjglkjoi43jig3j4",
            #     "collapse_key": "type_a",
            #     "content-available": true,
            #     "notification": {
            #         "title": "Someone has replied to you: ",
            #         "body": data['text']
            #     },
            #     "data": {
            #         "debate_id": data['debate_id']
            #     }
            # }

            # registration_id = "e6KtclvYdklimcK1PDOEGE:APA91bF4vHHQNBXCW5J-TzyuSl4EY4gai5G1N2qAUTleYv9aHTiKs6mNWexanM8PfBXhHFdBgadHbNdJdq75YkoMXKDNEJ2DeN3kd_4VsAw_lcZvgExQyc_HZtXzH5j3ToRUuO9dgPD_"
            # message_title = "Привет Артем"
            # message_body = "Только что ты получил первый пуш, поздравляю"
            # result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
            
            
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