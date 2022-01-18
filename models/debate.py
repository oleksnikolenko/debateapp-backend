import uuid
import datetime

from sqlalchemy import DateTime, select, func, or_, and_
from sqlalchemy.sql import text
from sqlalchemy.orm import column_property
from models.side import SideModel
from models.sidevote import SideVoteModel
from models.category import CategoryModel
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_imageattach.entity import Image, image_attachment
from db import db
from werkzeug.utils import cached_property

class DebateModel(db.Model):
    __tablename__ = 'debates'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    name = db.Column(db.String(255))
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)

    messages = db.relationship('MessageModel', lazy='dynamic', order_by="desc(MessageModel.created_date)", cascade='all, delete-orphan')
    favorites = db.relationship('FavoriteDebateModel')

    localization_name = db.Column(db.Text, db.ForeignKey('localizations.name'))
    localization = db.relationship('LocalizationModel')

    image = image_attachment('PictureModel', cascade='all,delete')
    debate_type = db.Column(db.String(40))
    promotion_type = db.Column(db.String(255))

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    leftside_id = db.Column(db.Text, db.ForeignKey('sides.id'))
    rightside_id = db.Column(db.Text, db.ForeignKey('sides.id'))

    leftside = db.relationship("SideModel", foreign_keys=[leftside_id], cascade='all')
    rightside = db.relationship("SideModel", foreign_keys=[rightside_id], cascade='all')

    ranking = db.Column(db.Integer, default=0)

    rating = column_property(
        select([func.count(SideVoteModel.id)]).\
            where(
                or_(
                    SideVoteModel.side_id==leftside_id,
                    SideVoteModel.side_id==rightside_id
                )
            ).scalar_subquery()
        )

    favorites = db.relationship('FavoriteDebateModel')

    def __init__(self, name, leftside_id, rightside_id, category_ids, localization_name, user_id, debate_type):
        self.name = name
        self.leftside_id = leftside_id
        self.rightside_id = rightside_id
        self.localization_name = localization_name
        self.user_id = user_id
        self.debate_type = debate_type
        for category_id in category_ids:
            category = CategoryModel.find_by_id(category_id)
            if category:
                self.tags.append(category)

    def json(self, user_id=None):
        from models.favoritedebate import FavoriteDebateModel
        replies_number = 0
        for message in self.messages:
            replies_number += message.replies.count()

        first_category = self.tags.first()

        return {
            'id': self.id,
            'name': self.name,
            'type': self.debate_type,
            'promotion_type': self.promotion_type,
            # TODO - remove hardcoded first category
            'category': first_category.json() if first_category else None,
            'image': self.image.locate() if self.image.original else None,
            'leftside': self.leftside.json(user_id) if self.leftside else None,
            'rightside': self.rightside.json(user_id) if self.rightside else None,
            'votes_count': self.rating,
            'is_favorite': True if FavoriteDebateModel.find_by_user_and_debate(user_id, self.id) else False,
            'message_count': self.messages.count() + replies_number,
            'message_list': {
                'messages': [message.json(user_id) for message in self.messages.paginate(1, 10, error_out=False).items],
                'has_next_page': self.messages.paginate(1, 10, error_out=False).has_next
            }
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def filter_by_localization(cls, localization_name, sorting):
        return cls.query.filter_by(localization_name=localization_name).order_by(*cls.sorting_method(sorting))

    @classmethod
    def filter_by_category_and_localization(cls, category_id, localization_name, sorting):
        category = CategoryModel.find_by_id(category_id)
        return cls.query\
            .filter_by(localization_name=localization_name)\
            .filter(cls.tags.contains(category))\
            .order_by(*cls.sorting_method(sorting))

    @classmethod
    def filter_by_context_and_localization(cls, context, localization_name):
        return cls.query\
            .filter_by(localization_name=localization_name)\
            .join(SideModel, or_(cls.leftside, cls.rightside))\
            .filter(or_(SideModel.name.ilike('%' + context + '%'), cls.name.ilike('%' + context + '%')))

    @classmethod
    def find_by_side_id(cls, side_id):
        return cls.query.filter(or_(cls.leftside_id==side_id, cls.rightside_id==side_id)).first()

    @classmethod
    def sorting_method(cls, sorting_method):
        if sorting_method == "newest":
            return (DebateModel.promotion_type.asc(), DebateModel.created_date.desc(),)
        elif sorting_method == "oldest":
             return (DebateModel.promotion_type.asc(), DebateModel.created_date.asc(),)
        # DEFAULT
        return (DebateModel.promotion_type.asc(), DebateModel.ranking.desc(), DebateModel.created_date.desc(),)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def get_opposite_side(self, side_id):
        if side_id == self.leftside_id:
            return self.rightside
        elif side_id == self.rightside_id:
            return self.leftside
        else:
            return None