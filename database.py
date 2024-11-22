from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///scandb.sqlite3'  # SQLite file database
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)