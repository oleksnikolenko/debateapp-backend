from flask_restful import Resource, reqparse
from models.sidevote import SideVoteModel
from models.debate import DebateModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity

class SideVote(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('debate_id', type=str, required=True, help="Debate_id is needed")
    parser.add_argument('side_id', type=str, required=True, help="Side_id is needed")

    @jwt_required
    def post(self):
        data = SideVote.parser.parse_args()
        user_uid = get_jwt_identity()
        user = UserModel.find_by_firebase_uid(user_uid)

        vote = SideVoteModel(data['side_id'], user.id)
        debate = DebateModel.find_by_id(data['debate_id'])

        if self.is_vote_in_debate(data['debate_id'], user.id):
            if SideVoteModel.is_vote_in_side(data['side_id'], user.id):
                vote = SideVoteModel.find_by_side_id(data['side_id'], user.id)
                try:
                    vote.delete_from_db()
                    return {
                        "debate": debate.json(user.id),
                        "message": "vote is successfully deleted"
                    }, 200
                except:
                    return {"message": "An error deleting this vote"}, 500
            else:
                debate = DebateModel.find_by_id(data['debate_id'])
                opposite_side = debate.get_opposite_side(data['side_id'])
                opposite_vote = SideVoteModel.find_by_side_id(opposite_side.id, user.id)
                opposite_vote.delete_from_db()

                try:
                    vote.save_to_db()
                except:
                    return {"message": "An error occured creating new or deleting vote"}, 500
        else:
            try:
                vote.save_to_db()
            except:
                return {"message": "An error occured creating new vote"}, 500

        return {
            "message": "vote is added successfully",
            "debate": debate.json(user.id)
        }, 201

    def is_vote_in_debate(self, debate_id, user_id):
        debate = DebateModel.find_by_id(debate_id)
        return SideVoteModel.is_vote_in_side(debate.leftside_id, user_id) or \
               SideVoteModel.is_vote_in_side(debate.rightside_id, user_id)
