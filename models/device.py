from db import db


class DeviceModel(db.Model):
    __tablename__ = 'devices'

    device_id = db.Column(db.String(40), primary_key=True)
    push_token = db.Column(db.String(255))

    localization_name = db.Column(db.Text, db.ForeignKey('localizations.name'))
    localization = db.relationship('LocalizationModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self, device_id, push_token, localization_name):
        self.device_id = device_id
        self.push_token = push_token
        self.localization_name = localization_name

    @classmethod
    def find_by_device_id(cls, device_id):
        return cls.query.filter_by(device_id=device_id).first()

    def save_to_db(self):
       db.session.add(self)
       db.session.commit()
