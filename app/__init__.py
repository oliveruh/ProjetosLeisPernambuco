from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def load_config(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')

    app.config['SENDER_EMAIL_USERNAME'] = os.environ.get('SENDER_EMAIL_USERNAME')
    app.config['SENDER_EMAIL_PASSWORD'] = os.environ.get('SENDER_EMAIL_PASSWORD')
    app.config['EMAIL_HOST'] = os.environ.get('EMAIL_HOST')
    app.config['EMAIL_PORT'] = os.environ.get('EMAIL_PORT')
    app.config['RECEIVER_EMAIL'] = os.environ.get('RECEIVER_EMAIL')

    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')

    app.config['S3_BUCKET'] = os.environ.get('S3_BUCKET')
    app.config['AWS_ACCESS_KEY'] = os.environ.get('AWS_ACCESS_KEY')
    app.config['AWS_SECRET_ACCESS_KEY'] = os.environ.get('AWS_SECRET_ACCESS_KEY')


def create_app():
    app = Flask(__name__)
    load_dotenv()
    load_config(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app import views
    app.register_blueprint(views.app)

    return app
