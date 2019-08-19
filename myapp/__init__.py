from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from myapp.config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__, static_url_path="/static")
app.config.from_object(Config)
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

from myapp.routes import *
