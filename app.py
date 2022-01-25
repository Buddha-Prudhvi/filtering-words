from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask_mail import Mail
from registerapi import api
from dashfiles import dash
from service import service

app = Flask(__name__)

app.register_blueprint(api)
app.register_blueprint(dash)
app.register_blueprint(service)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Welcome#123@localhost/gcs'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mail = Mail(app)

"""cors middleware"""
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

"""Mysql config"""
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Welcome#123'
app.config['MYSQL_DB'] = 'gcs'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

'''recaptcha configuration'''
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LcwUB8dAAAAAFduzTrHanvvw-lNsBxi5DqAj0-q'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LcwUB8dAAAAAK-shxFk7S6chxuynBaFoMiOAX9u'
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}

app.config['SECRET_KEY'] = 'secret123'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
mysql = MySQL(app)

"""creating models"""
class user_credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    userName = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

class REGISTER_DETAIL(db.Model):
    _id = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    fullName = db.Column(db.String(255), nullable=False)
    companyName = db.Column(db.String(255), nullable=False)
    companyWebsite = db.Column(db.String(255), nullable=False)
    userName = db.Column(db.String(100), unique=True,nullable=False)
    email = db.Column(db.String(100),nullable=False,unique=True)
    contact = db.Column(db.String(20), nullable=False,unique=True)
    password = db.Column(db.Text)
    address =  db.Column(db.String(255), nullable=False)
    def __init__(self, fullname, companyName,companyWebsite,userName,email,contact,address):
        self.fullname = fullname
        self.companyName = companyName
        self.companyWebsite = companyWebsite
        self.userName = userName
        self.email = email
        self.contact = contact
        self.address = address

class RECENT_FILES(db.Model):
    UID = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    Filename = db.Column(db.String(255),nullable = False)
    ServiceType = db.Column(db.String(255),nullable = False)
    PreviewLink = db.Column(db.String(255),nullable = False)
    Date = db.Column(db.Date,nullable = False)
    Status = db.Column(db.String(255),nullable = False)
    Download = db.Column(db.String(255),nullable = False)
    
    # def __repr__(self):
    #     return "<Comment %r>" % self.UID

class Subscription_Details(db.Model):
    UID = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    FID = db.Column(db.Integer, db.ForeignKey('REGISTER_DETAIL._id'),nullable=False)
    ProductName = db.Column(db.String(255),nullable = False)
    Subscriptions = db.Column(db.String(255),nullable = False)
    ExpiryDate = db.Column(db.Date,nullable = False)
    Status = db.Column(db.String(255),nullable = False)
    RemainingDays = db.Column(db.Integer,nullable = False)
    # def __repr__(self):
    #     return "<Comment %r>" % self.UID


class Usage(db.Model):
    UID = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    Keywords = db.Column(db.Integer,nullable = False)
    keywordTotal =db.Column(db.Integer,nullable = False)
    WordCloudUsage = db.Column(db.Integer,nullable = False)
    WordcloudTotal = db.Column(db.Integer,nullable = False)
    # def __repr__(self):
    #     return "<Comment %r>" % self.UID

class NEW_SERVICE(db.Model):
    UID = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    service_name = db.Column(db.String(255),nullable = False)
    subscription_type = db.Column(db.String(255),nullable = False)
    usage_value = db.Column(db.Integer,nullable = False)
    cost = db.Column(db.Integer,nullable = False)

class Billing_Details(db.Model):
    UID = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    FullName = db.Column(db.String(255),nullable = False)
    Email = db.Column(db.String(255),nullable = False)
    Mobile = db.Column(db.String(255),nullable = False)
    Country = db.Column(db.String(255),nullable = False)
    State = db.Column(db.String(255),nullable = False)
    City = db.Column(db.String(255),nullable = False)
    Zip_code = db.Column(db.Integer,nullable = False)
    GST = db.Column(db.Integer,nullable = True)
    
class upload_files(db.Model):
    id = db.Column(db.Integer,primary_key= True,autoincrement="auto")
    fid = db.Column(db.Integer, db.ForeignKey('REGISTER_DETAIL._id'),nullable=False)
    name = db.Column(db.String(300))
    file = db.Column(db.LargeBinary(length = (2**32)-1))
    extension = db.Column(db.String(15))
    ServiceType = db.Column(db.String(255),nullable = False,default="keywords")
    Date = db.Column(db.Date,nullable = False)
    Status = db.Column(db.String(255),nullable = False,default="success")
    output = db.Column(db.String(450))
    def __init__(self, name,file):
        self.name = name
        self.file = file

class custom_file(db.Model):
    id = db.Column(db.Integer,primary_key= True,autoincrement="auto")
    fid = db.Column(db.Integer, db.ForeignKey('REGISTER_DETAIL._id'),nullable=False)
    custom_file = db.Column(db.LargeBinary(length = (2**32)-1))
    def __init__(self,custom_file):
        self.custom_file = custom_file

if __name__ == '__main__':
    db.create_all()
    app.secret_key='secret123'
    app.run(host='192.168.235.117')
    # app.run(debug=True)
    

