from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigbrother.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class Members(db.Model):
    member_id = db.Column('member_id', db.Integer, primary_key=True)
    company_name = db.Column(db.String(200))
    name = db.Column(db.String(200))
    id_card = db.Column(db.String(200))
    address = db.Column(db.String(200))
    nationality = db.Column(db.String(200))
    begin_month = db.Column(db.String(200))
    end_month = db.Column(db.String(200))
    salary = db.Column(db.Float)
    injury = db.Column(db.String(200))
    endowment = db.Column(db.String(200))
    unemployment = db.Column(db.String(200))
    medical = db.Column(db.String(200))
    birth = db.Column(db.String(200))
    injury_check = db.Column(db.String(200))
    endowment_check = db.Column(db.String(200))
    unemployment_check = db.Column(db.String(200))
    medical_check = db.Column(db.String(200))
    birth_check = db.Column(db.String(200))
    is_valid = db.Column(db.String(200))
    person = db.Column(db.String(200))

    def __init__(self, company_name, name, id_card, address, nationality, begin_month, end_month,
                 salary, injury, endowment, unemployment, medical, birth,
                 injury_check, endowment_check, unemployment_check, medical_check, birth_check,
                 is_valid, person):
        self.company_name = company_name
        self.name = name
        self.id_card = id_card
        self.address = address
        self.nationality = nationality
        self.begin_month = begin_month
        self.end_month = end_month
        self.salary = salary
        self.injury = injury
        self.endowment = endowment
        self.unemployment = unemployment
        self.medical = medical
        self.birth = birth
        self.injury_check = injury_check
        self.endowment_check = endowment_check
        self.unemployment_check = unemployment_check
        self.medical_check = medical_check
        self.birth_check = birth_check
        self.is_valid = is_valid
        self.person = person
        db.create_all()