from flask import Flask
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_gravatar import Gravatar
from os import path


db = SQLAlchemy()
DB_NAME = "blog.db"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "kfjruv5d7931!sdwwwfhb2%"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User

    ckeditor = CKEditor(app)
    Bootstrap(app)

    gravatar = Gravatar(app, size=100, rating='g', default='retro',
                        force_default=False, force_lower=False,
                        use_ssl=False, base_url=None)

    create_database(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def create_database(app):
    if not path.exists("Blog/" + DB_NAME):
        db.create_all(app=app)
