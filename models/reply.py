import uuid
import datetime

from db import db
from datetime import timezone, date
from sqlalchemy import DateTime
from models.replyVote import ReplyVoteModel


class ReplyModel(db.Model):
    __tablename__ = 'replies'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    text = db.Column(db.String(2000))
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)
    is_edited = db.Column(db.Boolean, default=False)
    edited_date = db.Column(DateTime)

    thread_id = db.Column(db.Text, db.ForeignKey('messages.id'))
    thread = db.relationship('MessageModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    votes = db.relationship('ReplyVoteModel')

    def __init__(self, text, user_id, thread_id):
        self.text = text
        self.user_id = user_id
        self.thread_id = thread_id

    def json(self, user_id):
        positive_votes = [vote for vote in self.votes if vote.is_positive == True]
        negative_votes = [vote for vote in self.votes if vote.is_positive == False]
        user_vote = ReplyVoteModel.find_by_reply_and_user_id(self.id, user_id)
        if user_vote:
            user_vote = "up" if user_vote.is_positive else "down"
        else:
            user_vote = "none"
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'text': self.text,
            'user': self.user.json() if self.user else None,
            'created_time': self.created_date.replace(tzinfo=timezone.utc).timestamp(),
            'vote_count': len(positive_votes) - len(negative_votes),
            'user_vote': user_vote,
            'thread_message_count': 0,
            "thread_message_list": []
            # 'is_edited': self.is_edited,
            # 'edited_time': self.edited_date.replace(tzinfo=timezone.utc).timestamp() if self.edited_date else None
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_after_time(cls, thread_id, after_time):
        if after_time == 0:
            thread_messages = cls.query.filter(ReplyModel.thread_id == thread_id)
            return thread_messages.order_by(ReplyModel.created_date.desc())
        else:
            thread_messages = cls.query.filter(ReplyModel.thread_id == thread_id)
            return thread_messages.filter(ReplyModel.created_date < datetime.datetime.fromtimestamp(after_time)).order_by(ReplyModel.created_date.desc())


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
