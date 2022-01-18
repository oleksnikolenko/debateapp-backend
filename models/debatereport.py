from db import db

class DebateReportModel(db.Model):
    __tablename__ = 'debatereports'

    debate_id = db.Column(db.Text, db.ForeignKey('debates.id'), primary_key=True)
    debate = db.relationship('DebateModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship('UserModel')

    def __init__(self, debate_id, user_id):
        self.debate_id = debate_id
        self.user_id = user_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_debate_and_user_id(cls, debate_id, user_id):
        return cls.query.filter_by(debate_id=debate_id, user_id=user_id).first()
