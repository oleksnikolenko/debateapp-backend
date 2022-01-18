from db import db
from sqlalchemy_imageattach.entity import Image, image_attachment
import hashlib
import uuid


class PictureModel(db.Model, Image):
    __tablename__ = 'pictures'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)

    side_id = db.Column(db.Text, db.ForeignKey('sides.id'))
    side = db.relationship('SideModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    debate_id = db.Column(db.Text, db.ForeignKey('debates.id'))
    debate = db.relationship('DebateModel')

    @property
    def object_id(self):
        return int(hashlib.sha1(self.id.encode('utf-8')).hexdigest(), 16)
