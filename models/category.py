import uuid

from db import db
from models.localization import LocalizationModel


tag_assignment = db.Table('tag_assignment',
    db.Column('debate_id', db.Text, db.ForeignKey('debates.id')),
    db.Column('category_id', db.Text, db.ForeignKey('categories.id'))
)


class CategoryModel(db.Model):
    __tablename__ = 'categories'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    name = db.Column(db.String(80))
    rating = db.Column(db.Integer, default=0)

    localization_name = db.Column(db.Text, db.ForeignKey('localizations.name'))
    localization = db.relationship('LocalizationModel')

    tag_assignments = db.relationship('DebateModel', secondary=tag_assignment, backref=db.backref('tags', lazy='dynamic'))

    # debates = db.relationship('DebateModel')

    def __init__(self, name, localization_name):
        self.name = name
        self.localization_name = localization_name

    def json(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def filter_by_localization(cls, localization_name):
        return cls.query.filter_by(localization_name=localization_name).paginate(1, 20, error_out=False).items

    @classmethod
    def filter_by_context_and_localization(cls, context, localization_name):
        return cls.query\
            .filter_by(localization_name=localization_name)\
            .filter(cls.name.ilike('%' + context + '%'))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
