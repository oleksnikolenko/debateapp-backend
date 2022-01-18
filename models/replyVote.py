import uuid
import datetime

from db import db
from sqlalchemy import DateTime


class ReplyVoteModel(db.Model):
    __tablename__ = "replyvotes"

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)

    is_positive = db.Column(db.Boolean)

    reply_id = db.Column(db.Text, db.ForeignKey('replies.id'))
    reply = db.relationship('ReplyModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self, is_positive, reply_id, user_id):
        self.is_positive = is_positive
        self.reply_id = reply_id
        self.user_id = user_id

    @classmethod
    def find_by_reply_and_user_id(cls, reply_id, user_id):
        return cls.query.filter_by(reply_id=reply_id, user_id=user_id).first()

    @classmethod
    def find_number_of_votes(cls, reply_id):
        message_votes = cls.query.filter_by(reply_id=reply_id)
        positive_votes = message_votes.filter_by(is_positive=True).count()
        negative_votes = message_votes.filter_by(is_positive=False).count()
        return positive_votes - negative_votes


    @classmethod
    def is_vote_in_reply(cls, reply_id, user_id):
        return cls.query.filter(
            cls.reply_id == reply_id,
            cls.user_id == user_id
        ).count() > 0

    @classmethod
    def is_vote_positive(cls, reply_id, user_id):
        return cls.query.filter(
            cls.reply_id == reply_id,
            cls.user_id == user_id
        ).first().is_positive

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
