from flask import Flask
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_mail import Mail
from registerapi import api
from dashfiles import dash
from service import service
from wordservice import cloudservice
import jwt
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.register_blueprint(api)
app.register_blueprint(dash)
app.register_blueprint(service)
app.register_blueprint(cloudservice)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("MYSQL_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mail = Mail(app)

"""cors middleware"""
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

"""Mysql config"""
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

'''recaptcha configuration'''
app.config['RECAPTCHA_USE_SSL'] = False
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get("RECAPTCHA_PRIVATE_KEY")
app.config['RECAPTCHA_OPTIONS'] = {'theme': 'black'}

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
mysql = MySQL(app) 

"""creating models"""
class user_credentials(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    userName = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

class REGISTER_DETAIL(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    UUId = db.Column(db.String(50),unique = True)
    fullName = db.Column(db.String(255), nullable=False)
    companyName = db.Column(db.String(255), nullable=False)
    companyWebsite = db.Column(db.String(255), nullable=False)
    userName = db.Column(db.String(100), unique=True,nullable=False)
    email = db.Column(db.String(100),nullable=False,unique=True)
    contact = db.Column(db.String(20), nullable=False,unique=True)
    password = db.Column(db.Text)
    address =  db.Column(db.String(255), nullable=False)

class Usage(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    fid = db.Column(db.Integer,nullable=False)
    Keywords = db.Column(db.Integer)
    WordCloud = db.Column(db.Integer)
    KeywordTotal = db.Column(db.Integer)
    WordcloudTotal = db.Column(db.Integer)

class SERVICES(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    fid = db.Column(db.Integer,nullable=False)
    service_name = db.Column(db.String(255),nullable = False)
    subscription_type = db.Column(db.String(255),nullable = False)
    usage_value = db.Column(db.Integer,nullable = False)
    cost = db.Column(db.Integer,nullable = False)
    purchaseDate = db.Column(db.Date,nullable = False)
    time = db.Column(db.DateTime,nullable=False)
    ExpiryDate = db.Column(db.Date,nullable = False)
    status = db.Column(db.String(15))

class Billing_Details(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement="auto")
    fid = db.Column(db.Integer,nullable=False)
    payment_id = db.Column(db.String(255),nullable=False)
    FullName = db.Column(db.String(255),nullable = False)
    Email = db.Column(db.String(255),nullable = False)
    Mobile = db.Column(db.String(20),nullable = False)
    Country = db.Column(db.String(20),nullable = False)
    State = db.Column(db.String(255),nullable = False)
    City = db.Column(db.String(255),nullable = False)
    Zip_code = db.Column(db.String(100),nullable = False)
    GST = db.Column(db.String(100),nullable = True)
    
class upload_files(db.Model):
    id = db.Column(db.Integer,primary_key= True,autoincrement="auto")
    fid = db.Column(db.Integer,nullable=False)
    name = db.Column(db.String(300))
    file = db.Column(db.LargeBinary(length = (2**32)-1))
    filepath = db.Column(db.String(300))
    extension = db.Column(db.String(15))
    ServiceType = db.Column(db.String(255),nullable = False,default="keywords")
    Date = db.Column(db.DateTime,nullable = False)
    Status = db.Column(db.String(255),nullable = False,default="success")
    output = db.Column(db.String(450))
    keywords = db.Column(db.String(450))

class upload_word_files(db.Model):
    id = db.Column(db.Integer,primary_key= True,autoincrement="auto")
    fid = db.Column(db.Integer,nullable=False)
    file_name = db.Column(db.String(300))
    file = db.Column(db.LargeBinary(length = (2**32)-1))
    file_path = db.Column(db.String(300))
    extension = db.Column(db.String(15))
    Date = db.Column(db.DateTime,nullable = False)
    image_path =  db.Column(db.String(300))
    Status = db.Column(db.String(255),nullable = False,default="success")
    ServiceType = db.Column(db.String(255),nullable = False,default="keywords")
    keywords = db.Column(db.String(450))
    
class custom_file(db.Model):
    id = db.Column(db.Integer,primary_key= True,autoincrement="auto")
    fid = db.Column(db.Integer,nullable=False)
    custom_file = db.Column(db.LargeBinary(length = (2**32)-1))

if __name__ == '__main__':
    db.create_all()
    app.secret_key= os.environ.get("SECRET_KEY")
    app.run(host='192.168.235.153',debug=True)
    # app.run(debug=True)
    

