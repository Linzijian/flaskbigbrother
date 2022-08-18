from flask import Flask, request, flash, url_for, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from company import Companys
from member import Members
from report import Reports
from user import Users
from member_report import Member_reports
import datetime
from dateutil.relativedelta import relativedelta
import flask_excel as excel
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bigbrother.db'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


def get_cur_month():
    return datetime.datetime.now().strftime("%Y-%m")


def get_last_month(number, year, month, day):
    t = datetime.date(year, month, day)
    return (t - relativedelta(months=number)).strftime("%Y-%m")


def insurance_calculator_company(company_name, cur_month, em_payed_members=""):
    dic_company = {"injury_base": 0, "endowment_base": 0, "unemployment_base": 0, "medical_base": 0, "birth_base": 0,
                   "medical_c": 0, "medical_i": 0, "birth_c": 0, "birth_i": 0}
    members = Members.query.filter_by(company_name=company_name).all()
    company = Companys.query.filter_by(name=company_name).all()[0]
    m_base = {"injury_base": 3284, "injury_c": company.injury_ratio/100.0, "injury_i": 0,
              "endowment_base": 3284, "endowment_c": 0.16, "endowment_i": 0.08,
              "unemployment_base": 3284, "unemployment_c": 0.005, "unemployment_i": 0.005,
              "medical_base": 4374.6, "medical_c": 0.08, "medical_i": 0.02,
              "birth_base": 4374.6, "birth_c": 0.012, "birth_i": 0}
    dic_company["medical_c"] = 0
    dic_company["medical_i"] = 0
    dic_company["birth_c"] = 0
    dic_company["birth_i"] = 0
    for member in members:
        salary = member.salary
        if member.is_valid == "是" and member.begin_month <= cur_month and (member.end_month == "" or cur_month < member.end_month):
            if member.injury == "报":
                dic_company["injury_base"] += max(salary, m_base["injury_base"])
            if member.endowment == "报" and member.name not in em_payed_members.split(","):
                dic_company["endowment_base"] += max(salary, m_base["endowment_base"])
            if member.unemployment == "报":
                dic_company["unemployment_base"] += max(salary, m_base["unemployment_base"])
            if member.medical == "报" and member.name not in em_payed_members.split(","):
                dic_company["medical_base"] += max(salary, m_base["medical_base"])
                dic_company["medical_c"] += round(max(salary, m_base["medical_base"]) * m_base["medical_c"], 2)
                dic_company["medical_i"] += round(max(salary, m_base["medical_base"]) * m_base["medical_i"], 2)
            if member.birth == "报":
                dic_company["birth_base"] += max(salary, m_base["birth_base"])
                dic_company["birth_c"] += round(max(salary, m_base["birth_base"]) * m_base["birth_c"], 2)
                dic_company["birth_i"] += round(max(salary, m_base["birth_base"]) * m_base["birth_i"], 2)
    dic_company["injury_base"] = round(dic_company["injury_base"], 2)
    dic_company["endowment_base"] = round(dic_company["endowment_base"], 2)
    dic_company["unemployment_base"] = round(dic_company["unemployment_base"], 2)
    dic_company["medical_base"] = round(dic_company["medical_base"], 2)
    dic_company["birth_base"] = round(dic_company["birth_base"], 2)
    dic_company["injury_c"] = round(dic_company["injury_base"] * m_base["injury_c"], 2)
    dic_company["endowment_c"] = round(dic_company["endowment_base"] * m_base["endowment_c"], 2)
    dic_company["unemployment_c"] = round(dic_company["unemployment_base"] * m_base["unemployment_c"], 2)
    # dic_company["medical_c"] = round(dic_company["medical_base"] * m_base["medical_c"], 2)
    # dic_company["birth_c"] = round(dic_company["birth_base"] * m_base["birth_c"], 2)
    dic_company["injury_i"] = round(dic_company["injury_base"] * m_base["injury_i"], 2)
    dic_company["endowment_i"] = round(dic_company["endowment_base"] * m_base["endowment_i"], 2)
    dic_company["unemployment_i"] = round(dic_company["unemployment_base"] * m_base["unemployment_i"], 2)
    # dic_company["medical_i"] = round(dic_company["medical_base"] * m_base["medical_i"], 2)
    # dic_company["birth_i"] = round(dic_company["birth_base"] * m_base["birth_i"], 2)
    dic_company["predict_fee"] = round(dic_company["injury_c"] + dic_company["endowment_c"] + dic_company["unemployment_c"] +\
                                 dic_company["medical_c"] + dic_company["birth_c"] + dic_company["injury_i"] +\
                                 dic_company["endowment_i"] + dic_company["unemployment_i"] + dic_company["medical_i"] +\
                                 dic_company["birth_i"], 2)
    return dic_company


def insurance_calculator_members(company_name, cur_month, ill_members="", em_payed_members=""):
    member_data_dic = {}
    dic_company = {"injury_base": 0, "endowment_base": 0, "unemployment_base": 0, "medical_base": 0, "birth_base": 0,
                   "medical_c": 0, "medical_i": 0, "birth_c": 0, "birth_i": 0}
    members_list = []
    members = Members.query.filter_by(company_name=company_name).all()
    members_filter = []
    for member in members:
        if member.begin_month <= cur_month and (member.end_month == "" or cur_month <= member.end_month):
            members_filter.append(member)
    company = Companys.query.filter_by(name=company_name).all()[0]
    dic_result = get_cur_month_change_data_dic(cur_month)
    m_base = {"injury_base": 3284, "injury_c": company.injury_ratio/100.0, "injury_i": 0,
              "endowment_base": 3284, "endowment_c": 0.16, "endowment_i": 0.08,
              "unemployment_base": 3284, "unemployment_c": 0.005, "unemployment_i": 0.005,
              "medical_base": 4374.6, "medical_c": 0.08, "medical_i": 0.02,
              "birth_base": 4374.6, "birth_c": 0.012, "birth_i": 0}
    for member in members_filter:
        member_data = {"injury_base": 0, "endowment_base": 0, "unemployment_base": 0, "medical_base": 0, "birth_base": 0}
        salary = member.salary
        if member.is_valid == "是" and member.end_month == "":
            if member.injury == "报":
                dic_company["injury_base"] += max(salary, m_base["injury_base"])
                member_data["injury_base"] = max(salary, m_base["injury_base"])
            if member.endowment == "报" and member.name not in em_payed_members.split(","):
                dic_company["endowment_base"] += max(salary, m_base["endowment_base"])
                member_data["endowment_base"] = max(salary, m_base["endowment_base"])
            if member.unemployment == "报":
                dic_company["unemployment_base"] += max(salary, m_base["unemployment_base"])
                member_data["unemployment_base"] = max(salary, m_base["unemployment_base"])
            if member.medical == "报" and member.name not in em_payed_members.split(","):
                dic_company["medical_base"] += max(salary, m_base["medical_base"])
                member_data["medical_base"] = max(salary, m_base["medical_base"])
                dic_company["medical_c"] += round(max(salary, m_base["medical_base"]) * m_base["medical_c"], 2)
                dic_company["medical_i"] += round(max(salary, m_base["medical_base"]) * m_base["medical_i"], 2)
            if member.birth == "报":
                dic_company["birth_base"] += max(salary, m_base["birth_base"])
                member_data["birth_base"] = max(salary, m_base["birth_base"])
                dic_company["birth_c"] += round(max(salary, m_base["birth_base"]) * m_base["birth_c"], 2)
                dic_company["birth_i"] += round(max(salary, m_base["birth_base"]) * m_base["birth_i"], 2)
            member_data["ill"] = 0
            if member.name in ill_members.split(","):
                member_data["ill"] = 24

            member_data["injury_c"] = round(member_data["injury_base"] * m_base["injury_c"], 2)
            member_data["endowment_c"] = round(member_data["endowment_base"] * m_base["endowment_c"], 2)
            member_data["unemployment_c"] = round(member_data["unemployment_base"] * m_base["unemployment_c"], 2)
            member_data["medical_c"] = round(member_data["medical_base"] * m_base["medical_c"], 2)
            member_data["birth_c"] = round(member_data["birth_base"] * m_base["birth_c"], 2)
            member_data["injury_i"] = round(member_data["injury_base"] * m_base["injury_i"], 2)
            member_data["endowment_i"] = round(member_data["endowment_base"] * m_base["endowment_i"], 2)
            member_data["unemployment_i"] = round(member_data["unemployment_base"] * m_base["unemployment_i"], 2)
            member_data["medical_i"] = round(member_data["medical_base"] * m_base["medical_i"], 2)
            member_data["birth_i"] = round(member_data["birth_base"] * m_base["birth_i"], 2)
            member_data["sum_i"] = member_data["injury_i"] + member_data["endowment_i"] + member_data["unemployment_i"] + member_data["medical_i"] + member_data["birth_i"] + member_data["ill"]
            member_data["sum_c"] = member_data["injury_c"] + member_data["endowment_c"] + member_data["unemployment_c"] + member_data["medical_c"] + member_data["birth_c"]
            member_text = member.name.ljust(5, chr(12288)) + "单位部分: %.2f元\n"%(member_data["sum_c"]) + "".ljust(5, chr(12288)) + "个人部分:"
            if member_data["endowment_i"] > 0:
                member_text += " 养老%.2f元"%(member_data["endowment_i"])
            if member_data["medical_i"] > 0:
                member_text += " 医疗%.2f元" % (member_data["medical_i"])
            if member_data["unemployment_i"] > 0:
                member_text += " 失业%.2f元" % (member_data["unemployment_i"])
            if member_data["ill"] > 0:
                member_text += " 大病%.2f元" % (member_data["ill"])
            member_text += " 合计%.2f元"%(member_data["sum_i"])

            members_list.append(member_text)
            member_data_dic[member.name] = member_data
    dic_company["injury_c"] = round(dic_company["injury_base"] * m_base["injury_c"], 2)
    dic_company["endowment_c"] = round(dic_company["endowment_base"] * m_base["endowment_c"], 2)
    dic_company["unemployment_c"] = round(dic_company["unemployment_base"] * m_base["unemployment_c"], 2)
    # dic_company["medical_c"] = round(dic_company["medical_base"] * m_base["medical_c"], 2)
    # dic_company["birth_c"] = round(dic_company["birth_base"] * m_base["birth_c"], 2)
    dic_company["injury_i"] = round(dic_company["injury_base"] * m_base["injury_i"], 2)
    dic_company["endowment_i"] = round(dic_company["endowment_base"] * m_base["endowment_i"], 2)
    dic_company["unemployment_i"] = round(dic_company["unemployment_base"] * m_base["unemployment_i"], 2)
    # dic_company["medical_i"] = round(dic_company["medical_base"] * m_base["medical_i"], 2)
    # dic_company["birth_i"] = round(dic_company["birth_base"] * m_base["birth_i"], 2)
    dic_company["predict_fee_c"] = dic_company["injury_c"] + dic_company["endowment_c"] + dic_company["unemployment_c"] +\
                                   dic_company["medical_c"] + dic_company["birth_c"]
    dic_company["predict_fee_i"] = dic_company["injury_i"] + dic_company["endowment_i"] + dic_company["unemployment_i"] +\
                                   dic_company["medical_i"] + dic_company["birth_i"] + 24 * len(ill_members.split(","))
    head_str = dic_result[company_name]["description"]
    tail_str = "\n单位部分合计%.2f元, 个人部分合计%.2f元, 合计%.2f元. 明细如下:\n"%(dic_company["predict_fee_c"], dic_company["predict_fee_i"], dic_company["predict_fee_c"]+dic_company["predict_fee_i"])
    text = head_str + tail_str + "\n".join(members_list)
    return text, member_data_dic


def get_cur_month_change_data_dic(cur_month):
    dic_result = {}
    members = Members.query.all()
    last_month = get_last_month(1, int(cur_month[0:4]), int(cur_month[5:7]), 1)
    companys = Companys.query.all()
    for company in companys:
        dic_result[company.name] = {"last_month_cnt": 0, "cur_month_cnt": 0,
                                    "cur_month_add": 0, "cur_month_remove": 0,
                                    "last_month_members": [], "cur_month_members": [],
                                    "cur_month_add_m": [], "cur_month_remove_m": []}
    for member in members:
        # if member.is_valid == "是":
        if last_month >= member.begin_month and (member.end_month == "" or last_month < member.end_month):
            dic_result[member.company_name]["last_month_cnt"] += 1
            dic_result[member.company_name]["last_month_members"].append(member.name)
        if cur_month >= member.begin_month and (member.end_month == "" or cur_month < member.end_month):
            dic_result[member.company_name]["cur_month_cnt"] += 1
            dic_result[member.company_name]["cur_month_members"].append(member.name)
        if cur_month == member.begin_month:
            dic_result[member.company_name]["cur_month_add"] += 1
            dic_result[member.company_name]["cur_month_add_m"].append(member.name)
        if cur_month == member.end_month:
            dic_result[member.company_name]["cur_month_remove"] += 1
            dic_result[member.company_name]["cur_month_remove_m"].append(member.name)
    for company_name in dic_result:
        description = company_name + ", " + cur_month + ", 上月申报" + str(dic_result[company_name]["last_month_cnt"]) +\
        "人(" + ",".join(dic_result[company_name]["last_month_members"]) + ")"
        if dic_result[company_name]["cur_month_add"] > 0:
            description += ", 新增" + str(dic_result[company_name]["cur_month_add"]) +"人(" + ",".join(dic_result[company_name]["cur_month_add_m"]) + ")"
        if dic_result[company_name]["cur_month_remove"] > 0:
            description += ", 减少" + str(dic_result[company_name]["cur_month_remove"]) +"人(" + ",".join(dic_result[company_name]["cur_month_remove_m"]) + ")"
        description += ", 本月申报" + str(dic_result[company_name]["cur_month_cnt"]) + "人."
        dic_result[company_name]["description"] = description
    return dic_result


def validate_login(func):
    @wraps(func)
    def wrapper(**kwargs):
        if 'username' not in session:
            return render_template('refresh.html')
        else:
            return func(**kwargs)
    return wrapper


@app.route('/insurance_calculator')
@validate_login
def insurance_calculator():
    # if 'username' not in session:
    #     return redirect(url_for('home'))
    m_base = {"injury_base": 3284, "injury_c": 0.6, "injury_i": 0,
              "endowment_base": 3284, "endowment_c": 16, "endowment_i": 8,
              "unemployment_base": 3284, "unemployment_c": 0.5, "unemployment_i": 0.5,
              "medical_base": 4374.6, "medical_c": 8, "medical_i": 2,
              "birth_base": 4374.6, "birth_c": 1.2, "birth_i": 0}
    m_base["injury_c_fee"] = round(m_base["injury_base"]*m_base["injury_c"]/100, 2)
    m_base["injury_i_fee"] = round(m_base["injury_base"] * m_base["injury_i"]/100, 2)
    m_base["endowment_c_fee"] = round(m_base["endowment_base"] * m_base["endowment_c"]/100, 2)
    m_base["endowment_i_fee"] = round(m_base["endowment_base"] * m_base["endowment_i"]/100, 2)
    m_base["unemployment_c_fee"] = round(m_base["unemployment_base"] * m_base["unemployment_c"]/100, 2)
    m_base["unemployment_i_fee"] = round(m_base["unemployment_base"] * m_base["unemployment_i"]/100, 2)
    m_base["medical_c_fee"] = round(m_base["medical_base"] * m_base["medical_c"]/100, 2)
    m_base["medical_i_fee"] = round(m_base["medical_base"] * m_base["medical_i"]/100, 2)
    m_base["birth_c_fee"] = round(m_base["birth_base"] * m_base["birth_c"]/100, 2)
    m_base["birth_i_fee"] = round(m_base["birth_base"] * m_base["birth_i"]/100, 2)
    m_base["person_total"] = round(m_base["injury_i_fee"] + m_base["endowment_i_fee"] + m_base["unemployment_i_fee"] + m_base["medical_i_fee"] + m_base["birth_i_fee"], 2)
    m_base["company_total"] = round(m_base["injury_c_fee"] + m_base["endowment_c_fee"] + m_base["unemployment_c_fee"] + m_base["medical_c_fee"] + m_base["birth_c_fee"], 2)
    m_base["total_fee"] = round(m_base["person_total"] + m_base["company_total"], 2)
    return render_template('insurance_calculator.html', m_base=m_base)


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session["username"])


@app.route('/login', methods=['GET', 'POST'])
def login():
    text = ""
    if request.method == 'POST':
        user = Users.query.filter_by(name=request.form['name'], password=request.form['password']).all()
        if len(user) == 1:
            session['username'] = request.form['name']
            return redirect(url_for('home'))
        text = 'error'
    return render_template('login_new.html', text=text)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/company_update/<company_name>', methods=['GET', 'POST'])
@validate_login
def company_update(company_name):
    if request.method == 'POST':
        if not request.form['name'] or not request.form['position'] or not request.form['code']\
                or not request.form['zwwname'] or not request.form['scode'] or not request.form['person']\
                or not request.form['is_valid'] or not request.form['injury_ratio'] or not request.form['short_name']:
            flash('输入有误！', 'error')
        else:
            data = {"name": request.form['name'], "position": request.form['position'], "code": request.form['code'],
                    "zwwname": request.form['zwwname'], "scode": request.form['scode'], "injury_ratio": request.form['injury_ratio'],
                    "person": session['username'], "is_valid": request.form['is_valid'], "pay_type": request.form['pay_type'],
                    "short_name": request.form['short_name']}
            db.session.query(Companys).filter(Companys.name == company_name).update(data)
            db.session.commit()
            flash('修改成功！')
            return render_template('company_update.html',
                                   companys=Companys.query.filter_by(name=request.form['name']).all())
    return render_template('company_update.html',
                           companys=Companys.query.filter_by(name=company_name).all())


@app.route('/company_query', methods=['GET', 'POST'])
@validate_login
def company_query():
    if request.method == 'POST':
        if request.form['name'] != "":
            return render_template('company_query.html', name=request.form['name'],
                                   companys=Companys.query.filter_by(name=request.form['name']).all())
    return render_template('company_query.html', name="", companys=Companys.query.order_by(Companys.is_valid.desc()).all())


@app.route('/company_add', methods=['GET', 'POST'])
@validate_login
def company_add():
    if request.method == 'POST':
        if len(Companys.query.filter_by(name=request.form['name']).all()) > 0:
            flash('新增失败，公司简称不能重复！', 'error')
            render_template('company_add.html', request=request)
        elif len(Companys.query.filter_by(short_name=request.form['short_name']).all()) > 0:
            flash('新增失败，公司全称不能重复！', 'error')
            render_template('company_add.html', request=request)
        else:
            company = Companys(request.form['name'], request.form['position'], request.form['code'],
                               request.form['zwwname'], request.form['scode'], request.form['injury_ratio'],
                               session['username'], request.form['is_valid'], request.form['pay_type'],
                               request.form['short_name'])
            db.session.add(company)
            db.session.commit()
            flash('新增成功！')
            return redirect(url_for('company_query'))
    return render_template('company_add.html')


@app.route('/member_update/<member_id>', methods=['GET', 'POST'])
@validate_login
def member_update(member_id):
    if request.method == 'POST':
        if not request.form['company_name'] or not request.form['name'] or not request.form['id_card']\
                or not request.form['address'] or not request.form['nationality'] or not request.form['begin_month']\
                or not request.form['is_valid']:
            flash('输入有误！', 'error')
        else:
            data = {"company_name":request.form['company_name'], "name":request.form['name'], "id_card":request.form['id_card'],
                    "address":request.form['address'], "nationality":request.form['nationality'], "begin_month":request.form['begin_month'],
                    "end_month":request.form['end_month'], "salary":request.form['salary'], "injury":request.form['injury'],
                    "endowment": request.form['endowment'], "unemployment":request.form['unemployment'], "medical":request.form['medical'],
                    "birth": request.form['birth'], "injury_check":request.form['injury_check'], "endowment_check":request.form['endowment_check'],
                    "unemployment_check": request.form['unemployment_check'], "medical_check":request.form['medical_check'], "birth_check":request.form['birth_check'],
                    "is_valid":request.form['is_valid'], "person": session['username']}
            db.session.query(Members).filter(Members.member_id == request.form['member_id']).update(data)
            db.session.commit()
            flash('修改成功！')
            return render_template('member_update.html',
                                   members=Members.query.filter_by(member_id=request.form['member_id']).all(),
                                   companys=Companys.query.all(),
                                   cur_month=get_cur_month())
    return render_template('member_update.html',
                           members=Members.query.filter_by(member_id=member_id).all(),
                           companys=Companys.query.all(),
                           cur_month=get_cur_month())
                           # cur_month = "2022-06")


@app.route('/member_query/<company_name>', methods=['GET', 'POST'])
@validate_login
def member_query(company_name):
    if request.method == 'POST':
        if request.form['name'] == "" or request.form['company_name'] == "":
            if request.form['name'] == "" and request.form['company_name'] == "":
                return render_template('member_query.html', company_name="", name="", members=Members.query.all(), cur_month=get_cur_month())
            if request.form['name'] == "":
                return render_template('member_query.html', name=request.form['name'], company_name=request.form['company_name'],
                                       members=Members.query.filter_by(company_name=request.form['company_name']).all(), cur_month=get_cur_month())
            if request.form['company_name'] == "":
                return render_template('member_query.html', name=request.form['name'], company_name=request.form['company_name'],
                                       members=Members.query.filter_by(name=request.form['name']).all(), cur_month=get_cur_month())
        else:
            return render_template('member_query.html', name=request.form['name'], company_name=request.form['company_name'],
                                   members=Members.query.filter_by(name=request.form['name'], company_name=request.form['company_name']).all(), cur_month=get_cur_month())
    if company_name == "all":
        return render_template('member_query.html', company_name="", name="", members=Members.query.all(), cur_month=get_cur_month())
    else:
        return render_template('member_query.html', name="", company_name=company_name,
                               members=Members.query.filter_by(company_name=company_name).order_by(Members.begin_month.asc()).all(),
                               cur_month=get_cur_month())


@app.route('/member_add/<company_name>', methods=['GET', 'POST'])
@validate_login
def member_add(company_name):
    if request.method == 'POST':
        if len(Members.query.filter_by(id_card=request.form['id_card'], company_name=request.form['company_name']).all()) > 0:
            flash('新增失败，%s公司已包含身份证号为%s的人员！'%(request.form['company_name'], request.form['id_card']), 'error')
            return render_template('member_add.html', companys=Companys.query.all(),
                                   cur_month=get_cur_month(), request=request)
        else:
            member = Members(request.form['company_name'], request.form['name'], request.form['id_card'],
                             request.form['address'], request.form['nationality'], request.form['begin_month'],
                             request.form['end_month'], request.form['salary'],
                             request.form['injury'], request.form['endowment'],
                             request.form['unemployment'], request.form['medical'],
                             request.form['birth'],
                             request.form['injury_check'], request.form['endowment_check'],
                             request.form['unemployment_check'], request.form['medical_check'],
                             request.form['birth_check'],
                             request.form['is_valid'], session['username'])
            db.session.add(member)
            db.session.commit()
            flash('新增成功！')
            return redirect(url_for('member_query', company_name="all"))
    if company_name != "all":
        return render_template('member_add.html', companys=Companys.query.filter_by(is_valid='是', name=company_name).all(), cur_month=get_cur_month())
    return render_template('member_add.html', companys=Companys.query.filter_by(is_valid='是').all(),
                           cur_month=get_cur_month())

@app.route('/report_progress/<name>', methods=['GET', 'POST'])
@validate_login
def report_progress(name):
    cur_month = get_cur_month()
    # cur_month = "2022-06"
    m_change_data = get_cur_month_change_data_dic(cur_month)
    reports = Reports.query.filter_by(cur_month=cur_month).all()
    for company_name in m_change_data:
        m_change_data[company_name]["members_check"] = "进行中"
        m_change_data[company_name]["reportable_check"] = "未开始"
        m_change_data[company_name]["report_state"] = "未开始"
        m_change_data[company_name]["pay_state"] = "未开始"
    for report in reports:
        if report.members_check == "已完成":
            m_change_data[report.company_name]["members_check"] = "已完成"
            m_change_data[report.company_name]["reportable_check"] = "进行中"
        if report.reportable_check == "已完成":
            m_change_data[report.company_name]["reportable_check"] = "已完成"
            m_change_data[report.company_name]["report_state"] = "进行中"
        if report.report_state == "已完成":
            m_change_data[report.company_name]["report_state"] = "已完成"
            m_change_data[report.company_name]["pay_state"] = "进行中"
        if report.pay_state == "已完成" and report.pay_list_print == "已完成":
            m_change_data[report.company_name]["pay_state"] = "已完成"
    if request.method == 'POST':
        if cur_month <= request.form['cur_month']:
            m_change_data = get_cur_month_change_data_dic(request.form['cur_month'])
            reports = Reports.query.filter_by(cur_month=request.form['cur_month']).all()
            for company_name in m_change_data:
                m_change_data[company_name]["members_check"] = "进行中"
                m_change_data[company_name]["reportable_check"] = "未开始"
                m_change_data[company_name]["report_state"] = "未开始"
                m_change_data[company_name]["pay_state"] = "未开始"
            for report in reports:
                if report.members_check == "已完成":
                    m_change_data[report.company_name]["members_check"] = "已完成"
                    m_change_data[report.company_name]["reportable_check"] = "进行中"
                if report.reportable_check == "已完成":
                    m_change_data[report.company_name]["reportable_check"] = "已完成"
                    m_change_data[report.company_name]["report_state"] = "进行中"
                if report.report_state == "已完成":
                    m_change_data[report.company_name]["report_state"] = "已完成"
                    m_change_data[report.company_name]["pay_state"] = "进行中"
                if report.pay_state == "已完成" and report.pay_list_print == "已完成":
                    m_change_data[report.company_name]["pay_state"] = "已完成"
            companys = Companys.query.filter_by(name=request.form['name'], is_valid="是").all()
            if request.form['name'] == "":
                companys = Companys.query.all()
            return render_template('report_progress.html', name=request.form['name'],
                                   companys=companys,
                                   cur_month=request.form['cur_month'],
                                   m_change_data=m_change_data)
        else:
            m_change_data = {}
            reports = Reports.query.filter_by(cur_month=request.form['cur_month']).all()
            for report in reports:
                if report.company_name not in m_change_data:
                    m_change_data[report.company_name] = {}
                if report.members_check == "已完成":
                    m_change_data[report.company_name]["members_check"] = "已完成"
                    m_change_data[report.company_name]["reportable_check"] = "进行中"
                if report.reportable_check == "已完成":
                    m_change_data[report.company_name]["reportable_check"] = "已完成"
                    m_change_data[report.company_name]["report_state"] = "进行中"
                if report.report_state == "已完成":
                    m_change_data[report.company_name]["report_state"] = "已完成"
                    m_change_data[report.company_name]["pay_state"] = "进行中"
                if report.pay_state == "已完成" and report.pay_list_print == "已完成":
                    m_change_data[report.company_name]["pay_state"] = "已完成"
                m_change_data["last_month_cnt"] = report.last_month_cnt
                m_change_data["cur_month_cnt"] = report.cur_month_cnt
                m_change_data["cur_month_add"] = report.cur_month_add
                m_change_data["cur_month_remove"] = report.cur_month_remove
            companys = Companys.query.filter_by(name=request.form['name']).all()
            if request.form['name'] == "":
                companys = Companys.query.all()
            company_filter = []
            for company in companys:
                if company.name in m_change_data:
                    company_filter.append(company)
            return render_template('report_progress.html', name=request.form['name'],
                                   companys=company_filter,
                                   cur_month=request.form['cur_month'],
                                   m_change_data=m_change_data)

    companys = Companys.query.filter_by(name=name, is_valid="是").all()
    if name == "all":
        companys = Companys.query.filter_by(is_valid="是").all()
        name = ""
    return render_template('report_progress.html', name=name,
                           companys=companys,
                           cur_month=cur_month,
                           m_change_data=m_change_data)


@app.route('/confirm_member/<name>/<readonly>/<cur_month>', methods=['GET', 'POST'])
@validate_login
def confirm_member(name, readonly, cur_month):
    m_change_data = get_cur_month_change_data_dic(cur_month)
    company_data = {"company_name": name,
                    "cur_month": cur_month,
                    "last_month_cnt": m_change_data[name]["last_month_cnt"],
                    "cur_month_cnt": m_change_data[name]["cur_month_cnt"],
                    "cur_month_add": m_change_data[name]["cur_month_add"],
                    "cur_month_remove": m_change_data[name]["cur_month_remove"],
                    "description": m_change_data[name]["description"]}
    members = Members.query.filter_by(company_name=name).order_by(Members.begin_month.asc()).all()
    members_filter = []
    for member in members:
        if member.begin_month <= cur_month and ( member.end_month == "" or cur_month <= member.end_month):
            members_filter.append(member)
    if request.method == 'POST':
        m_change_data = get_cur_month_change_data_dic(cur_month)[name]
        company = Companys.query.filter_by(name=name).all()[0]
        report = Reports(cur_month, name, company.code, company.zwwname, company.scode,
                         m_change_data["last_month_cnt"], m_change_data["cur_month_cnt"],
                         m_change_data["cur_month_add"], m_change_data["cur_month_remove"],
                         "已完成", request.form['name'])
        db.session.add(report)
        db.session.commit()
        flash(name + '， 已完成名单确认！')
        return redirect(url_for('report_progress', name=name, readonly=readonly))
    members_check_person = ""
    if 'username' in session:
        members_check_person = session['username']
    report_data = Reports.query.filter_by(company_name=name, cur_month=cur_month).all()
    if len(report_data) > 0:
        members_check_person = report_data[0].members_check_person
    return render_template('confirm_member.html',
                           members=members_filter,
                           company_data=company_data,
                           company=Companys.query.filter_by(name=name).all(),
                           readonly=readonly,
                           members_check_person=members_check_person)


@app.route('/reportable_check/<name>/<readonly>/<cur_month>', methods=['GET', 'POST'])
@validate_login
def reportable_check(name, readonly, cur_month):
    report_data = Reports.query.filter_by(company_name=name, cur_month=cur_month).all()[0]
    members = Members.query.filter_by(company_name=name).all()
    members_filter = []
    for member in members:
        if member.begin_month <= cur_month and (member.end_month == "" or cur_month <= member.end_month):
            members_filter.append(member)
    all_valid = True
    for member in members_filter:
        if member.is_valid == "否":
            all_valid = False
    if request.method == 'POST':
        data = {"reportable_check_person": request.form['name'], "reportable_check": "已完成"}
        db.session.query(Reports).filter(and_(Reports.company_name == name, Reports.cur_month == cur_month)).update(data)
        db.session.commit()

        flash(name + '， 已完成可申报确认！')
        return redirect(url_for('report_progress', name=name))
    if report_data.reportable_check_person == "":
        report_data.reportable_check_person = session['username']
    return render_template('reportable_check.html',
                           members=members_filter,
                           report_data=report_data,
                           all_valid=all_valid,
                           company=Companys.query.filter_by(name=name).all(),
                           readonly=readonly)


def write_member_report(c_name, cur_month, ill_members, em_payed_members):
    text, member_data_dic = insurance_calculator_members(c_name, cur_month, ill_members, em_payed_members)
    members = Members.query.filter_by(company_name=c_name, end_month="", is_valid='是').all()
    for member in members:
        name = member.name
        company_name = c_name
        salary = member.salary
        id_card = member.id_card
        injury = 0
        endowment = member_data_dic[name]["endowment_i"]
        # if name in em_payed_members.split(","):
        #     endowment = 0
        unemployment = member_data_dic[name]["unemployment_i"]
        medical = member_data_dic[name]["medical_i"]
        # if name in em_payed_members.split(","):
        #     medical = 0
        birth = 0
        ill = member_data_dic[name]["ill"]
        member_report = Member_reports(name, company_name, id_card, cur_month, salary, injury, endowment, unemployment, medical, birth, ill)
        db.session.add(member_report)
        db.session.commit()


@app.route('/report_check/<name>/<readonly>/<cur_month>', methods=['GET', 'POST'])
@validate_login
def report_check(name, readonly, cur_month):
    report_data = Reports.query.filter_by(company_name=name, cur_month=cur_month).all()[0]
    if request.method == 'POST':
        real_fee = 0
        if request.form['real_fee'] != "":
            real_fee = float(request.form['real_fee'])
        ill_members = request.form.getlist("ill_members")
        ill_members_list = []
        # print("ill_members:", ill_members)
        for ill_member in ill_members:
            ill_members_list.append(ill_member.split("_")[0])
        cur_month_members = Members.query.filter_by(company_name=name, is_valid='是', end_month="").all()
        ill_cnt = len(ill_members)
        ill_all = "否"
        if len(request.form.getlist("ill_all")) > 0:
            ill_cnt = request.form['ill_all']
            ill_all = "是"
            ill_members_list = []
            for member in cur_month_members:
                ill_members_list.append(member.name)
        # print("ill_cnt:", ill_cnt)
        em_payed_members_list = []
        em_payed_members = request.form.getlist("em_payed_members")
        # print("em_payed_members:", em_payed_members)
        for member in em_payed_members:
            em_payed_members_list.append(member.split("_")[0])
        report_state = "未完成"
        # print(real_fee, float(request.form['predict_fee']), real_fee == float(request.form['predict_fee']))
        if request.form['injury'] == "完成" and request.form['endowment'] == "完成" and request.form['unemployment'] == "完成" and request.form['medical'] == "完成" and\
            request.form['birth'] == "完成" and abs(real_fee - float(request.form['predict_fee'])) < 0.0001:
            report_state = "已完成"
        # print("report_state:", report_state)
        # print("predict_fee:", request.form['predict_fee'])
        data = {"injury": request.form['injury'],
                "endowment": request.form['endowment'],
                "unemployment": request.form['unemployment'],
                "medical": request.form['medical'],
                "birth": request.form['birth'],
                "ill_cnt": ill_cnt,
                "predict_fee": float(request.form['predict_fee']),
                "real_fee": real_fee,
                "reason_text": request.form['reason_text'],
                "report_state": report_state,
                "report_person": session['username'],
                "ill_all": ill_all,
                "ill_members": ",".join(ill_members_list),
                "em_payed_members": ",".join(em_payed_members_list)}
        db.session.query(Reports).filter(and_(Reports.company_name == name, Reports.cur_month == cur_month)).update(data)
        db.session.commit()
        if report_state == "已完成":
            flash(name + '，已完成申报确认！')
            return redirect(url_for('report_progress', name=name))
        else:
            flash('修改完成！')
            return redirect(url_for('report_check', name=name, readonly=readonly, cur_month=cur_month))
    if report_data.report_person == "":
        report_data.report_person = session['username']
    text, member_data_dic = insurance_calculator_members(name, cur_month)
    dic_company = insurance_calculator_company(name, cur_month)
    if report_data.predict_fee == 0:
        report_data.predict_fee = dic_company['predict_fee']
    return render_template('report_check.html',
                           report_data=report_data,
                           company=Companys.query.filter_by(name=name).all(),
                           dic_company=dic_company,
                           readonly=readonly,
                           cur_add_members=Members.query.filter_by(company_name=name, begin_month=cur_month, is_valid='是').all(),
                           endowment_medical_members=Members.query.filter_by(company_name=name, begin_month=cur_month, is_valid='是', endowment="报", medical="报").all(),
                           member_data_dic=member_data_dic)


@app.route('/pay_check/<name>/<readonly>/<cur_month>', methods=['GET', 'POST'])
@validate_login
def pay_check(name, readonly, cur_month):
    report_data = Reports.query.filter_by(company_name=name, cur_month=cur_month).all()[0]
    if request.method == 'POST':
        data = {"pay_type": request.form['pay_type'],
                "pay_list_print": request.form['pay_list_print'],
                "pay_state": request.form['pay_state'],
                "pay_check_person": request.form['pay_check_person']}
        db.session.query(Reports).filter(and_(Reports.company_name == name, Reports.cur_month == cur_month)).update(data)
        db.session.commit()
        if request.form['pay_state'] == "已完成" and request.form['pay_list_print'] == "已完成":
            flash(name + '，已完成缴费确认！')
            write_member_report(name, cur_month, report_data.ill_members, report_data.em_payed_members)
            return redirect(url_for('report_progress', name=name))
        else:
            flash('修改完成！')
            return redirect(url_for('pay_check', name=name, readonly=readonly, cur_month=cur_month))
    if report_data.pay_check_person == "":
        report_data.pay_check_person = session["username"]
    company = Companys.query.filter_by(name=name).all()
    if report_data.pay_type == "":
        report_data.pay_type = company[0].pay_type
    text, member_data_dic = insurance_calculator_members(name, cur_month, report_data.ill_members, report_data.em_payed_members)
    return render_template('pay_check.html',
                           report_data=report_data,
                           company=company,
                           dic_company=insurance_calculator_company(name, cur_month, report_data.em_payed_members),
                           text=text,
                           readonly=readonly)


@app.route('/company_pay_history/<company_name>', methods=['GET', 'POST'])
@validate_login
def company_pay_history(company_name):
    return render_template('company_pay_history.html',
                           company_name=company_name,
                           reports=Reports.query.filter_by(company_name=company_name).order_by(Reports.cur_month.asc()).all())


@app.route('/member_pay_history/<id_card>', methods=['GET', 'POST'])
@validate_login
def member_pay_history(id_card):
    name = Members.query.filter_by(id_card=id_card).all()[0].name
    member_reports = Member_reports.query.filter_by(id_card=id_card).order_by(Member_reports.cur_month.asc()).all()
    for member in member_reports:
        member.birth = round(member.endowment + member.unemployment + member.medical + member.ill, 2)
    return render_template('member_pay_history.html',
                           name=name,
                           member_reports=member_reports)


@app.route("/export_member_record/<cur_month>", methods=['GET'])
@validate_login
def export_member_record(cur_month):
    content = [['序号', '公司名称', '姓名', '工资', '绩效', '应发工资', '养老（个人）', '失业（个人）', '医保（个人）', '大病（个人）', '公积金（个人）', '实发工资']]
    member_reports = Member_reports.query.filter_by(cur_month=cur_month).all()
    i = 1
    for member in member_reports:
        line = [i, member.company_name, member.name, member.salary, "", "", member.endowment, member.unemployment, member.medical, member.ill, "", ""]
        content.append(line)
        i += 1
    return excel.make_response_from_array(content, "xlsx", file_name=cur_month)


if __name__ == "__main__":
    companys = Companys("1", "1", "1", "1", "1", 0.6, "1", "1", "1", "1")
    members = Members("1", "1", "1", "1", "1", "1", "1", 3000,
                      "1", "1", "1", "1", "1", "1", "1", "1", "1", "1",
                      "1", "1")
    reports = Reports("1", "1", "1", "1", "1", 0, 0, 0, 0, "1", "1")
    member_reports = Member_reports("1", "1", "1", "1", 0, 0, 0, 0, 0, 0, 0)
    db.create_all()
    excel.init_excel(app)
    app.run(debug=True, port=80, host="0.0.0.0")
    # app.run(port=80, host="0.0.0.0")