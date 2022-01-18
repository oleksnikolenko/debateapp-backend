import uuid
import datetime

from db import db
from sqlalchemy import DateTime


class MessageVoteModel(db.Model):
    __tablename__ = "messagevotes"

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)

    is_positive = db.Column(db.Boolean)
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    message_id = db.Column(db.Text, db.ForeignKey('messages.id'))
    message = db.relationship('MessageModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self, is_positive, message_id, user_id):
        self.is_positive = is_positive
        self.message_id = message_id
        self.user_id = user_id

    @classmethod
    def find_by_message_and_user_id(cls, message_id, user_id):
        return cls.query.filter_by(message_id=message_id, user_id=user_id).first()

    @classmethod
    def find_number_of_votes(cls, message_id):
        message_votes = cls.query.filter_by(message_id=message_id)
        positive_votes = message_votes.filter_by(is_positive=True).count()
        negative_votes = message_votes.filter_by(is_positive=False).count()
        return positive_votes - negative_votes

    @classmethod
    def is_vote_in_message(cls, message_id, user_id):
        return cls.query.filter(
            cls.message_id == message_id,
            cls.user_id == user_id
        ).count() > 0

    @classmethod
    def is_vote_positive(cls, message_id, user_id):
        return cls.query.filter(
            cls.message_id == message_id,
            cls.user_id == user_id
        ).first().is_positive

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
