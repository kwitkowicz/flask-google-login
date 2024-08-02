import os

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from api.auth import auth
from api.home import home

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
SECRET_KEY = os.environ.get("SECRET_KEY", None)
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", None)

db = SQLAlchemy()
migrate = Migrate()

from api.models import User


def create_app(test_config=None):
    print(SQLALCHEMY_DATABASE_URI)
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID,
        GOOGLE_DISCOVERY_URL=GOOGLE_DISCOVERY_URL,
        GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET

    )

    db.init_app(app)
    with app.app_context():
        db.create_all()
        db.session.commit()
    migrate.init_app(app, db)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.unauthorized_handler
    def unauthorized():
        return "You must be logged in to access this content.", 403

    # Flask-Login helper to retrieve a user from our db
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    app.register_blueprint(home.home_blueprint)
    app.register_blueprint(auth.auth_blueprint)

    app.add_url_rule('/', endpoint='index')

    return app
