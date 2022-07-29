from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigbrother.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class Companys(db.Model):
    company_id = db.Column('company_id', db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    position = db.Column(db.String(200))
    code = db.Column(db.String(200))
    sbpass = db.Column(db.String(200))
    bapass = db.Column(db.String(200))
    zwwname = db.Column(db.String(200))
    zwwpass = db.Column(db.String(200))
    scode = db.Column(db.String(200))
    injury_ratio = db.Column(db.Float)
    person = db.Column(db.String(200))
    is_valid = db.Column(db.String(200))

    def __init__(self, name, position, code, sbpass, bapass, zwwname, zwwpass, scode, injury_ratio, person, is_valid):
        self.name = name
        self.position = position
        self.code = code
        self.sbpass = sbpass
        self.bapass = bapass
        self.zwwname = zwwname
        self.zwwpass = zwwpass
        self.scode = scode
        self.injury_ratio = injury_ratio
        self.person = person
        self.is_valid = is_valid
        db.create_all()