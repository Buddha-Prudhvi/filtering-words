from codecs import encode
import random
from flask import Blueprint, request, session, jsonify,Flask
from flask_mail import Mail,Message
from itsdangerous import base64_decode
from flask_cors import cross_origin
from passlib.hash import sha256_crypt
import base64
from flask_mysqldb import MySQL

app = Flask(__name__)
api = Blueprint('api', __name__)

"""mail configuration"""
app.config['MAIL_SERVER'] = 'webmail.prospectatech.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'gcs__mailer@prospectatech.com'
app.config['MAIL_PASSWORD'] = 'Welc0me@gcs21'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['USER_ENABLE_EMAIL'] = True

mysql = MySQL(app)
mail = Mail(app)

"""Register endPoint"""
@api.route('/api/register',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def register():
    if request.method == 'POST':
        global fullName
        fullName = request.json['fullName']
        companyName = request.json['companyName']
        companyWebsite = request.json['companyWebsite']
        userName = request.json['userName']
        global email
        email = request.json['email']
        contact = request.json['phoneNumber']
        address = request.json['address']
        session['userdetails'] = [fullName,companyName,companyWebsite,userName,email,contact,address]
        listToStr = ','.join(map(str, session['userdetails']))
        sample_string_bytes = listToStr.encode("ascii")
        base64_bytes = base64.b64encode(sample_string_bytes)
        global id
        id = base64_bytes.decode('utf-8')
        cur = mysql.connection.cursor()
        res1 = cur.execute("SELECT userName FROM REGISTER_DETAIL WHERE userName= %s",[userName])
        res2 = cur.execute("SELECT email FROM REGISTER_DETAIL WHERE email= %s",[email])
        res3 = cur.execute("SELECT contact FROM REGISTER_DETAIL WHERE contact= %s",[contact])
        mysql.connection.commit()
        cur.close()
        if res1 != 0:
            return jsonify({'success': False,'message': 'Username already exists'})
        if res2 != 0:
            return jsonify({'success': False,'message': 'Email address already exists'})
        if res3 != 0:
            return jsonify({'success': False,'message': 'Phone Number already exists'})
        if (res1 and res2 and res3) == 0:
            sendmaail()
            if 'userdetails' in session:
                session.pop('userdetails',None)
        return jsonify({'success': True,'message': 'Activation Email sent to your registered email address'})
    return jsonify({"Success":False,"msg":"Bad request"})

"""Sending Mail Method"""
@api.route('/api/resendmail',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def sendmaail():
    msg = Message(
        subject="Welcome to GCS.",
        sender="gcs__mailer@prospectatech.com",
        recipients=[email])
    url = "http://192.168.235.145:4200/createpassword?token={}".format(id)
    msg.html = '''<img href="https://drive.google.com/file/d/1szvb_gGVBta4dibM-UhB3Vt1Qpdcxel5/view?usp=drivesdk">
                <br><br><h3 >Hi {}</h3><br><br> <p>You are receiving this e-mail because you have registered a new account on GCS.<br><br>
                    We can’t wait for you to start using GCS Suite and seeing results in your business.<br><br>
                    Simply <a href={}> click Here</a> to get started, or visit our Help Center www.gcs-suite.com/help to learn more about how to use GCS Suite.
            <br><br> As always, our support team can be reached at support@gcs.com if you ever get stuck.
            <br><br><br><br>Have a great day!
            <br><br>Team GCS</p>'''.format(fullName, url)
    mail.send(msg)
    return jsonify({'success': True, 'message': 'Resent Activation Mail Successfully'})

"""storing data"""
@api.route('/api/storeregister',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def dcrypt_storage():
    if request.method == 'POST':
        decode_string = request.json['token']
        pas = request.json['password']
        base64_bytes = decode_string.encode("ascii")
        sample_string_bytes = base64.b64decode(base64_bytes)
        sample_string = sample_string_bytes.decode("ascii")
        list_1 = sample_string.split(',')
        list_1 = sample_string.split(',')
        fullName = list_1[0]
        companyName = list_1[1]
        companyWebsite = list_1[2]
        userName =  list_1[3]
        email = list_1[4]
        contact = list_1[5]
        addres = list_1[6:]
        address = ','.join(addres)
        password = sha256_crypt.hash(pas)
        cur = mysql.connection.cursor()
        res1 = cur.execute("SELECT userName FROM REGISTER_DETAIL WHERE userName= %s", [userName])
        if res1 == 0:
            cur.execute("INSERT INTO REGISTER_DETAIL(fullName,companyName,companyWebsite,userName,email,contact,password,address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",[fullName, companyName, companyWebsite, userName, email, contact, password, address])
            cur.execute("INSERT INTO user_credentials(userName,password) VALUES (%s,%s)", (userName, password))
            mysql.connection.commit()
            cur.close()
            return jsonify({'success': True, 'message': 'User Sucessfully Registered'})
        else:
            return jsonify({'success': False, 'message': "User already Registered please login"})
    return jsonify({"success":False,'message':'Registration Failed'})

"""Login endpoint """
@api.route('/api/login', methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        userName = request.json['userName']
        password_candidate = request.json['password']
        recaptcha = request.json['recaptcha']
        # Create cursor
        cur = mysql.connection.cursor()
        # Get user by username
        result = cur.execute("SELECT * FROM user_credentials WHERE userName = %s", [userName])
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate,password):
                # Passed
                session['logged_in'] = True
                session['userName'] = userName
                id=data['id']
                encode_id = base64.b64encode(str(id).encode('ascii'))
                idd = encode_id.decode('utf-8')
                # decode_id = base64_decode(encode_id.decode('ascii'))
                global user
                user  = session['userName']
                return jsonify({'success':True,'message':'Login Successfull','id':idd})
            else:
                return jsonify({'success':False,'message':'Invalid User Credentials'})
        else:
            return jsonify({'success':False,'message':'Username not found'})
    return jsonify({"success":False,"message":"Welcome to login"})

"""sending email to reset password"""
@api.route('/api/emailreset',methods= ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def password_mail():
    session['Email'] = request.json['email']
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email FROM REGISTER_DETAIL WHERE email = %s",[session['Email']])
    if res > 0:
        email = session['Email']
        sample_string_bytes = email.encode("ascii")
        base64_bytes = base64.b64encode(sample_string_bytes)
        id = base64_bytes.decode("ascii")
        msg = Message(
            subject="Welcome to GCS.",
            sender="gcs__mailer@prospectatech.com",
            recipients=[email])
        url = "http://192.168.235.145:4200/email?token={}".format(id)
        msg.html = '''To reset your password please click here <a href= "{}">click Here</a>'''.format(url)
        mail.send(msg)
        return jsonify({"success":True,"message":"Email sent to your Registered Email"})
    else:
        return jsonify({"success":False,"message":"Enter Registered Email"})

"""update password through email"""
@api.route('/api/resetpassword',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def reset_password():
    if request.method == 'POST':
        confirm_password = request.json['confirm_password']
        decode_string = request.json['token']
        new_password = sha256_crypt.hash(confirm_password)
        base = decode_string.encode("ascii")
        decode_string_bytes = base64.b64decode(decode_string)
        sample_string = decode_string_bytes.decode("ascii")
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM REGISTER_DETAIL WHERE email = %s", [sample_string])
        result = cur.fetchone()
        userName = result.get('userName')
        password = result.get('password')
        cur.close()
        if res>0:
            if sha256_crypt.verify(confirm_password, password) == True:
                return jsonify({'sucess':False,'message':"New Password can't be same as old password"})
            else:
                cur = mysql.connection.cursor()
                cur.execute("UPDATE REGISTER_DETAIL SET password = %s WHERE userName = %s",(new_password,userName))
                cur.execute("UPDATE user_credentials SET password = %s WHERE userName = %s",(new_password,userName))
                mysql.connection.commit()
                cur.close()
                return jsonify({'success':True,'message':'Password Updated Succesfully'})
        else:
            return jsonify({'success':False,'message':'Enter Regsitered email'})
    return jsonify({'success':False,'message':'Bad Request'})

"""sending otp to mobile"""
@api.route('/api/sendotp',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def sendmobile_otp():
    global mobilenum
    mobilenum = request.json['phoneNumber']
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT contact FROM REGISTER_DETAIL WHERE contact = %s", [mobilenum])
    if res > 0:
        global x
        otp = random.randint(0000,9999)
        session['otp'] = otp
        x = session['otp']
        if 'otp' in session:
            session.pop('otp',None)
        return jsonify({'success': True, 'message': 'otp sent,{}'.format(otp)})
    else:
        return jsonify({'success':False,'message':'Enter Registered Mobile Number'})

"""resending otp to mobile"""
@api.route('/api/resendotp',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def resendmobile_otp():
    otp1 = random.randint(0000,9999)
    session['otp1'] = otp1
    global y
    y = session['otp1']
    return jsonify({'success': True, 'message': 'OTP Resent Successfully,{}'.format(otp1)})

"""otp validating"""
@api.route('/api/validateotp',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def validate_otp():
    otp = request.json['otp']
    otp_to_int = int(otp)
    if x == otp_to_int:
        return jsonify({'success':True,'message':'OTP validated successfully'})
    elif y == otp_to_int:
        return jsonify({'success':True,'message':'OTP validated successfully'})
    else:
        return jsonify({'success':False,'message':'Please Enter Valid OTP'})

"""reseting password by otp"""
@api.route('/api/resetpassotp',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def updatepass_otp():
    confirm_password = request.json['confirm_password']
    new_password = sha256_crypt.hash(confirm_password)
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT contact,password,userName FROM REGISTER_DETAIL WHERE contact = %s", [mobilenum])
    result = cur.fetchone()
    userName = result.get('userName')
    password = result.get('password')
    cur.close()
    if res>0:
        if sha256_crypt.verify(confirm_password,password):
            return jsonify({'success':False,'message':"New Password can't be same as old password"})
        else:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE REGISTER_DETAIL SET password = %s WHERE userName = %s", (new_password, userName))
            cur.execute("UPDATE user_credentials SET password = %s WHERE userName = %s", (new_password, userName))
            mysql.connection.commit()
            globals()['x'] = None
            globals()['y'] = None
            return jsonify({'success':True,'message':'Password Successfully Updated'})
    return jsonify({'success':False,'message':"Mobile number Doesn't exist"})

@api.route('/api/getregister',methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def getregisterdata():
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT fullName,companyName FROM REGISTER_DETAIL WHERE userName = %s",[user])
        result = cur.fetchone()
        cur.close()
        return jsonify({'success':True,'result':result})
    return jsonify({'success':False})

@api.route('/api/logout',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def log_out():
    session.pop('userName', None)
    return jsonify({'success': True, 'result': "You successfully logged out"})
    return jsonify ({'success':False})