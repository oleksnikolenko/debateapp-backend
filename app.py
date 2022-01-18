import os

from flask import Flask
from flask_restful import Api

from resources.debate import Debate, DebateList, DebateCreator
from resources.message import Message, MessageList
from resources.messageVote import MessageVote
from resources.user import UserRegister, UserList, UserRefresh, UserEdit
from resources.sidevote import SideVote
from resources.category import Category, CategoryList
from resources.favoritedebate import FavoriteDebate
from resources.device import Device
from resources.search import Search
from resources.contactus import ContactUs
from resources.termsofuse import TermsOfUse
from resources.debatereport import DebateReport
from resources.category import CategorySearch
from resources.debate_ranking import DebateRanking
from resources.userfeedback import UserFeedback
from resources.privacypolicy import PrivacyPolicy
from sqlalchemy_imageattach.context import (pop_store_context,
                                            push_store_context)
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://alex:765834@localhost:5432/alex'#os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SERVER_NAME'] = 'whocooler.live'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string1488'
app.config['PROPAGATE_EXCEPTIONS'] = True
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/var/www/html/debates-rest/debates-rest-api-production/debates-rest-api-29faa-firebase-adminsdk-dvtkk-91cb5ac230.json"
app.secret_key = 'jose'
jwt = JWTManager(app)
api = Api(app)

fs_store = HttpExposedFileSystemStore(
    '/var/www/html/debates-rest/debates-rest-api-production/images',
    'images/',
    host_url_getter=lambda:'https://{0}/'.format(app.config['SERVER_NAME'])
)

app.wsgi_app = fs_store.wsgi_middleware(app.wsgi_app)

@app.before_request
def start_implicit_store_context():
    push_store_context(fs_store)

@app.teardown_request
def stop_implicit_store_context(exception=None):
    pop_store_context()

api.add_resource(Debate, '/debate')
api.add_resource(DebateList, '/<string:localization>/debates')
api.add_resource(UserRegister, '/register')
api.add_resource(Message, '/message')
api.add_resource(UserList, '/users')
api.add_resource(SideVote, '/vote')
api.add_resource(Category, '/<string:localization>/category')
api.add_resource(CategoryList, '/<string:localization>/categories')
api.add_resource(UserRefresh, '/refresh')
api.add_resource(DebateCreator, '/<string:localization>/debatecreate')
api.add_resource(MessageList, '/messages')
api.add_resource(MessageVote, '/messagevote')
api.add_resource(UserEdit, '/useredit')
api.add_resource(FavoriteDebate, '/favorites')
api.add_resource(Device, '/pingdevice')
api.add_resource(Search, '/<string:localization>/search')
api.add_resource(ContactUs, '/contactus')
api.add_resource(TermsOfUse, '/terms')
api.add_resource(DebateReport, '/debatereport')
api.add_resource(CategorySearch, '/<string:localization>/categorysearch')
api.add_resource(DebateRanking, '/debateranking')
api.add_resource(UserFeedback, '/soup')
api.add_resource(PrivacyPolicy, '/privacy')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
