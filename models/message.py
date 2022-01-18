import uuid
import datetime

from db import db
from datetime import timezone, date
from sqlalchemy import DateTime
from models.messageVote import MessageVoteModel
from models.reply import ReplyModel
from models.user import UserModel
from models.messageVote import MessageVoteModel


class MessageModel(db.Model):
    __tablename__ = 'messages'

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    text = db.Column(db.String(2000))
    created_date = db.Column(DateTime, default=datetime.datetime.utcnow)
    is_edited = db.Column(db.Boolean, default=False)
    edited_date = db.Column(DateTime)

    replies = db.relationship('ReplyModel', lazy='dynamic', order_by="desc(ReplyModel.created_date)", cascade='all,delete-orphan')

    debate_id = db.Column(db.Text, db.ForeignKey('debates.id'))
    debate = db.relationship('DebateModel')

    user_id = db.Column(db.Text, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    message_votes = db.relationship('MessageVoteModel')

    def __init__(self, text, user_id, debate_id):
        self.text = text
        self.user_id = user_id
        self.debate_id = debate_id

    def json(self, user_id):
        positive_votes = [vote for vote in self.message_votes if vote.is_positive == True]
        negative_votes = [vote for vote in self.message_votes if vote.is_positive == False]
        user_vote = MessageVoteModel.find_by_message_and_user_id(self.id, user_id)
        if user_vote:
            user_vote = "up" if user_vote.is_positive else "down"
        else:
            user_vote = "none"
        return {
            'id': self.id,
            # 'parent_id': None,
            'text': self.text,
            'user': self.user.json() if self.user else None,
            'created_time': self.created_date.replace(tzinfo=timezone.utc).timestamp(),
            'vote_count': len(positive_votes) - len(negative_votes),
            'user_vote': user_vote,
            'thread_message_count': self.replies.count(),
            'thread_message_list': [],#[reply.json(user_id) for reply in self.messages.paginate(1, 10, error_out=False).items],
            # 'replies_number': len(self.replies) if self.replies else 0
            # 'thread_message': self.replies[0].json() if self.replies else None,
            # 'is_edited': self.is_edited,
            # 'edited_time': self.edited_date.replace(tzinfo=timezone.utc).timestamp() if self.edited_date else None
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_after_time(cls, debate_id, after_time):
        debate_messages = cls.query.filter(MessageModel.debate_id == debate_id)
        return debate_messages.filter(MessageModel.created_date < datetime.datetime.fromtimestamp(after_time)).order_by(MessageModel.created_date.desc())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
