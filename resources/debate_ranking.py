from flask_restful import Resource
from models.debate import DebateModel
from models.sidevote import SideVoteModel
from models.message import MessageModel
from datetime import datetime, timedelta, date
from sqlalchemy import or_


class DebateRanking(Resource):
    
    def post(self):
        debates = DebateModel.query.all()

        # ranking_period = datetime.now() - timedelta(days=7)

        # for debate in debates:
        #     votes_count = SideVoteModel.query.filter(or_(SideVoteModel.side_id==debate.leftside_id, SideVoteModel.side_id==debate.rightside_id)).filter(SideVoteModel.created_date>ranking_period).count()
        #     message_count = MessageModel.query.filter_by(debate_id=debate.id).filter(MessageModel.created_date>ranking_period).count()

        #     ranking_count = votes_count + message_count * 2

        #     debate.ranking = ranking_count
        #     debate.save_to_db()

        # return {'message': 'Success'}, 200
        for debate in debates:
            ranking = 0

            votes = SideVoteModel.query.filter(or_(SideVoteModel.side_id==debate.leftside_id, SideVoteModel.side_id==debate.rightside_id))
            messages = MessageModel.query.filter_by(debate_id=debate.id)

            for vote in votes:
                delta = datetime.now() - vote.created_date
                days = delta.days

                ranking += pow(1/2, days) * 100

            for message in messages:
                delta = datetime.now() - message.created_date
                days = delta.days

                ranking += pow(1/2, days) * 200

            debate.ranking = ranking
            debate.save_to_db()

        return {'message': 'Success'}, 200
