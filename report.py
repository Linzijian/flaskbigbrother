from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigbrother.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)

# 基础信息： cur_month,company_name,code,zwwname,scode,last_month_cnt,cur_month_cnt,cur_month_add,cur_month_remove,
# 增减确认、可申报确认： members_check,members_check_person,reportable_check,reportable_check_person,
# 五险申报： injury,endowment,unemployment,medical,birth,ill_cnt,predict_fee,real_fee,reason_text,report_state,report_person,
# 缴费确认： pay_type,pay_list_print,pay_state,pay_check_person

class Reports(db.Model):
    report_id = db.Column('report_id', db.Integer, primary_key=True)
    cur_month = db.Column('cur_month', db.String(200))
    company_name = db.Column('company_name', db.String(200))
    code = db.Column(db.String(200))
    zwwname = db.Column(db.String(200))
    scode = db.Column(db.String(200))
    last_month_cnt = db.Column(db.Integer)
    cur_month_cnt = db.Column(db.Integer)
    cur_month_add = db.Column(db.Integer)
    cur_month_remove = db.Column(db.Integer)
    members_check = db.Column(db.String(200))
    members_check_person = db.Column(db.String(200))
    reportable_check = db.Column(db.String(200))
    reportable_check_person = db.Column(db.String(200))
    injury = db.Column(db.String(200))
    endowment = db.Column(db.String(200))
    unemployment = db.Column(db.String(200))
    medical = db.Column(db.String(200))
    birth = db.Column(db.String(200))
    ill_cnt = db.Column(db.Integer)
    predict_fee = db.Column(db.Float)
    real_fee = db.Column(db.Float)
    reason_text = db.Column(db.String(200))
    report_state = db.Column(db.String(200))
    report_person = db.Column(db.String(200))
    pay_type = db.Column(db.String(200))
    pay_list_print = db.Column(db.String(200))
    pay_state = db.Column(db.String(200))
    pay_check_person = db.Column(db.String(200))
    UniqueConstraint(cur_month, company_name, name='uix_1')

    def __init__(self, cur_month, company_name, code, zwwname, scode, last_month_cnt, cur_month_cnt, cur_month_add,
                 cur_month_remove, members_check, members_check_person, reportable_check="不可申报",
                 reportable_check_person="", injury="其他", endowment="其他", unemployment="其他", medical="其他", birth="其他",
                 ill_cnt=0, predict_fee=0, real_fee=0, reason_text="",
                 report_state="未完成",report_person="",pay_type="",pay_list_print="",pay_state="未完成",pay_check_person=""):
        self.cur_month = cur_month
        self.company_name = company_name
        self.code = code
        self.zwwname = zwwname
        self.scode = scode
        self.last_month_cnt = last_month_cnt
        self.cur_month_cnt = cur_month_cnt
        self.cur_month_add = cur_month_add
        self.cur_month_remove = cur_month_remove
        self.members_check = members_check
        self.members_check_person = members_check_person
        self.reportable_check = reportable_check
        self.reportable_check_person = reportable_check_person
        self.injury = injury
        self.endowment = endowment
        self.unemployment = unemployment
        self.medical = medical
        self.birth = birth
        self.ill_cnt = ill_cnt
        self.predict_fee = predict_fee
        self.real_fee = real_fee
        self.reason_text = reason_text
        self.report_state = report_state
        self.report_person = report_person
        self.pay_type = pay_type
        self.pay_list_print = pay_list_print
        self.pay_state = pay_state
        self.pay_check_person = pay_check_person
        db.create_all()