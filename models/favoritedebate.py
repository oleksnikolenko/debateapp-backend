from db import db
from models.debate import DebateModel

class FavoriteDebateModel(db.Model):
    __tablename__ = 'favoritedebates'

    debate_id = db.Column(db.Text, db.ForeignKey('debates.id', ondelete="CASCADE"), primary_key=True)
    debate = db.relationship('DebateModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('UserModel')

    def __init__(self, debate_id, user_id):
        self.debate_id = debate_id
        self.user_id = user_id

    def json(self, user_id):
        return self.debate.json(user_id)

    @classmethod
    def filter_by_user_id(cls, user_id, sorting):
        return cls.query.filter_by(user_id=user_id).join(DebateModel).order_by(cls.sorting_method(sorting))

    @classmethod
    def find_by_user_and_debate(cls, user_id, debate_id):
        return cls.query.filter_by(user_id=user_id, debate_id=debate_id).first()

    @classmethod
    def sorting_method(cls, sorting_method):
        if sorting_method == "newest":
            return DebateModel.created_date.desc()
        elif sorting_method == "oldest":
             return DebateModel.created_date.asc()
        # DEFAULT
        return DebateModel.rating.desc()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()