from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigbrother.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class Users(db.Model):
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    password = db.Column(db.String(200))

    def __init__(self, name, password):
        self.name = name
        self.password = password
        db.create_all()