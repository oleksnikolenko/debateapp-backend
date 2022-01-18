from app import app
from db import db
import pyrebase
import firebase_admin

db.init_app(app)

config = {
    "apiKey": "AIzaSyAkJvtYrg3mUhKFluM0cGAZfY_NSAqu5_k",
    "authDomain": "debates-rest-api-29faa.firebaseapp.com",
    "databaseURL": "https://debates-rest-api-29faa.firebaseio.com",
    "projectId": "debates-rest-api-29faa",
    "storageBucket": "debates-rest-api-29faa.appspot.com",
    "messagingSenderId": "264606055840",
    "appId": "1:264606055840:web:96f2b25f5e2ea0c75678c5",
    "measurementId": "G-G0W15WDBYV"
}

firebase = pyrebase.initialize_app(config)

firebase_admin.initialize_app()

with app.app_context():
     db.create_all()

@app.before_first_request
def create_tables():
     db.create_all()