from db import db
from models.device import DeviceModel

class LocalizationModel(db.Model):
    __tablename__ = 'localizations'

    name = db.Column(db.String(2), primary_key=True)

    debates = db.relationship('DebateModel')
    devices = db.relationship('DeviceModel')
