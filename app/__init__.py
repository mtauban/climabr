from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object('config')
    db.init_app(app)
    return app

app = create_app()


from app import views, models