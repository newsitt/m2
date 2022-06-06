from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    sector = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=False), default=func.now())
    add_info = db.relationship('Info')
    # notes = db.relationship('Note')


class Info(db.Model):
    # auto generated
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # from form
    zone = db.Column(db.String(100))
    sector_name = db.Column(db.String(200), unique=True)
    sector_type = db.Column(db.String(200))
    lat = db.Column(db.Float, unique=True)
    long = db.Column(db.Float, unique=True)
    address = db.Column(db.String(500))
    population = db.Column(db.Float)
    housing = db.Column(db.Float)
    amount_waste = db.Column(db.Float)
    amount_waste_kg = db.Column(db.Float)
    edit_date = db.Column(db.String(50))
    # from calculation
    waste_rate = db.Column(db.Float)
    housing_size = db.Column(db.Float)
    income = db.Column(db.Float)
