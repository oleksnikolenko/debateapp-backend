import sqlite3
import uuid
import datetime

from db import db
from sqlalchemy import DateTime
from sqlalchemy_imageattach.entity import image_attachment
from models.picture import PictureModel

class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    username = db.Column(db.String(80))
    firebase_uid = db.Column(db.String(255))
    avatar_url = db.Column(db.String(255))
    platform = db.Column(db.String(12))
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)
    is_banned = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    avatar = image_attachment('PictureModel', cascade='all,delete-orphan')

    messages = db.relationship('MessageModel', lazy='dynamic')
    votes = db.relationship('SideVoteModel', lazy='dynamic')
    favorites = db.relationship('FavoriteDebateModel', lazy='dynamic')
    devices = db.relationship('DeviceModel', lazy='dynamic')

    def __init__(self, username, firebase_uid, avatar_url, platform=None):
        self.username = username
        self.firebase_uid = firebase_uid
        self.avatar_url = avatar_url
        self.platform = platform

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'avatar_url': self.avatar.locate() if self.avatar.original else self.avatar_url
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_firebase_uid(cls, firebase_uid):
        return cls.query.filter_by(firebase_uid=firebase_uid).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()
