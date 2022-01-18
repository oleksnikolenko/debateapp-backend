import uuid
import datetime

from db import db
from sqlalchemy import DateTime

class SideVoteModel(db.Model):
    __tablename__ = 'sidevotes'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)

    side_id = db.Column(db.Text, db.ForeignKey('sides.id'))
    side = db.relationship('SideModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, side_id, user_id):
        self.side_id = side_id
        self.user_id = user_id

    @classmethod
    def find_by_side_id(cls, side_id, user_id):
        return cls.query.filter_by(side_id=side_id, user_id=user_id).first()

    @classmethod
    def is_vote_in_side(cls, side_id, user_id):
        return cls.query.filter_by(
            side_id=side_id,
            user_id=user_id).count() > 0

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()