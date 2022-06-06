from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
# import pandas as pd
# import sqlite3
from .dashboard import create_dash_application
from .mapapp import create_dash_map_application

db = SQLAlchemy()
DB_NAME = 'database.db'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "m2dev"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .dashboard import dashboard
    from .mapapp import mapapp

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(dashboard, url_preix='/')
    app.register_blueprint(mapapp, url_prefix='/')

    from .models import User, Info

    create_database(app)
    create_dash_application(app)
    create_dash_map_application(app)

    # # import csv records to a table in database
    # df = pd.read_csv(
    #     'https://raw.githubusercontent.com/newsitt/m2-showcase/main/all.csv')
    # # print(df.head())
    # connection = sqlite3.connect(
    #     r'C:\Users\PC-01\Desktop\m2_project\app\database.db')
    # df.to_sql(name='info', con=connection, if_exists='append', index=False)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app


def create_database(app):
    if not path.exists('m2_project/' + DB_NAME):
        # delete all data in columns in order to recreate a new database
        # db.drop_all(app=app)
        # create all tables into database
        db.create_all(app=app)
        print('Database has been created!')
