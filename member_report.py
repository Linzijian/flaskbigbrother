from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigbrother.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class Member_reports(db.Model):
    member_report_id = db.Column('member_report_id', db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    cur_month = db.Column(db.String(200))
    salary = db.Column(db.Float)
    injury = db.Column(db.Float)
    endowment = db.Column(db.Float)
    unemployment = db.Column(db.Float)
    medical = db.Column(db.Float)
    birth = db.Column(db.Float)
    ill = db.Column(db.Float)

    def __init__(self, name, company_name, cur_month, salary, injury, endowment, unemployment, medical, birth, ill):
        self.name = name
        self.company_name = company_name
        self.cur_month = cur_month
        self.salary = salary
        self.injury = injury
        self.endowment = endowment
        self.unemployment = unemployment
        self.medical = medical
        self.birth = birth
        self.ill = ill
        db.create_all()