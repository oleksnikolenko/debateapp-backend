from flask_restful import Resource, reqparse, inputs
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.messageVote import MessageVoteModel
from models.replyVote import ReplyVoteModel
from models.user import UserModel


class MessageVote(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('is_positive', type=inputs.boolean)
    parser.add_argument('message_id', type=str)
    parser.add_argument('thread_id', type=str)

    @jwt_required
    def post(self):
        data = MessageVote.parser.parse_args()
        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        print("POS:", data['is_positive'])

        parent_id = data['thread_id']

        if parent_id:
            message_vote = ReplyVoteModel.find_by_reply_and_user_id(parent_id, user.id)
        else:
            message_vote = MessageVoteModel.find_by_message_and_user_id(data['message_id'], user.id)

        if message_vote:
            message_vote.is_positive = data['is_positive']
            message_vote.save_to_db()
            # try:
            #     message_vote.is_positive = data['is_positive']
            #     message_vote.save_to_db()
            # except:
            #     return {"error": "cannot change a vote"}, 500
        else:
            if parent_id:
                message_vote = ReplyVoteModel(data['is_positive'], parent_id, user.id)
            else:
                message_vote = MessageVoteModel(data['is_positive'], data['message_id'], user.id)
            message_vote.save_to_db()
            # try:
            #     message_vote.save_to_db()
            # except:
            #     return {'error': "An error occured creating new vote"}, 500

        if message_vote.is_positive == True:
            vote_type = "up"
        else:
            vote_type = "down"

        if parent_id:
            vote_count = ReplyVoteModel.find_number_of_votes(parent_id)
        else:
            vote_count = MessageVoteModel.find_number_of_votes(data["message_id"])

        return {
            "vote_type": vote_type,
            "object_id": message_vote.id, 
            "vote_count": vote_count
        }, 201

    @jwt_required
    def delete(self):
        data = MessageVote.parser.parse_args()
        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        parent_id = data['thread_id']

        if parent_id:
            message_vote = ReplyVoteModel.find_by_reply_and_user_id(parent_id, user.id)
        else:
            message_vote = MessageVoteModel.find_by_message_and_user_id(data['message_id'], user.id)
           
        message_vote.delete_from_db()

        if parent_id:
            vote_count = vote_count = ReplyVoteModel.find_number_of_votes(parent_id)
        else:
            vote_count = MessageVoteModel.find_number_of_votes(data["message_id"])
    
        return {
            "vote_type": "none",
            "object_id": message_vote.id, 
            "vote_count": vote_count,
            "message": "successfully deleted"
        }, 200
