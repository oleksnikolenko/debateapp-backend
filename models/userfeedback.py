from db import db

class UserFeedbackModel(db.Model):
    __tablename__ = 'userfeedback'

    id = db.Column(db.Integer, primary_key=True)    
    key = db.Column(db.String(2000))
    text = db.Column(db.String(2000))

    def __init__(self, key, text):
        self.key = key
        self.text = text

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()