from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from myapp.config import Config

app = Flask(__name__, static_url_path="/static")
app.config.from_object(Config)
db = SQLAlchemy(app)

from myapp.routes import *
