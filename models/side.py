from db import db
from sqlalchemy_imageattach.entity import Image, image_attachment
from models.picture import PictureModel
from models.sidevote import SideVoteModel
import uuid

class SideModel(db.Model):
    __tablename__ = 'sides'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    name = db.Column(db.String(80))
    image = image_attachment('PictureModel', cascade='all,delete')

    votes = db.relationship('SideVoteModel')

    def __init__(self, name):
        self.name = name

    def json(self, user_id):
        return {
        'id': self.id,
        'name': self.name,
        'rating_count': len(self.votes),
        'image': self.image.locate() if self.image.original else None,
        'is_voted_by_user': SideVoteModel.query.filter(
            SideVoteModel.side_id == self.id,
            SideVoteModel.user_id == user_id
        ).count() > 0 if user_id else False
    }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_debate_id(cls, debate_id):
        return cls.query.filter_by(debate_id=debate_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
