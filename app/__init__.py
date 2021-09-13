from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login = LoginManager(app)
login.login_view = 'login'
moment = Moment(app)
mail = Mail(app)
db.init_app(app)
migrate.init_app(app, db)
login.init_app(app)
moment.init_app(app)


# def create_app(config_class=Config):

#     return app


from app import routes, models 