from crypt import methods
from operator import methodcaller
from flask import Flask,Blueprint,request,jsonify,session
from flask_mysqldb import MySQL
from flask_cors import cross_origin
import datetime
# from mysqlx import Auth
from passlib.hash import sha256_crypt
from auth import token_required,innerkeywords,verifyactive
import razorpay

app = Flask(__name__)
dash = Blueprint('dash', __name__)

mysql = MySQL(app)

@dash.route('/api/password_reset_by_old',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def password_reset_by_old(current_user):
    if request.method == "POST":
        try:
            old_password = request.json['old_password']
            new_password = request.json['new_password']
            hash_new_pass = sha256_crypt.hash(new_password)
            cur = mysql.connection.cursor()
            res = cur.execute("SELECT * FROM REGISTER_DETAIL WHERE id =%s",[current_user])
            if res>0:
                result = cur.fetchone()
                old_pass = result.get("password")
                userName = result.get("userName")
                if sha256_crypt.verify(old_password,old_pass) == True:
                    if sha256_crypt.verify(new_password,old_pass) == True:
                        return jsonify({"success":True,"message":"new password shouldnt be same as ol password"})
                    else:
                        cur.execute("UPDATE REGISTER_DETAIL SET password = %s WHERE userName = %s",(hash_new_pass,userName))
                        cur.execute("UPDATE user_credentials SET password = %s WHERE userName = %s",(hash_new_pass,userName))
                        mysql.connection.commit()
                        cur.close()
                        return jsonify({'success':True,'message':'Password Updated Succesfully'})
                else:
                    return jsonify({'success':True,'message':'old password is incorrect'})
        except:
            return jsonify({"success":False})
    return jsonify({'success':False})

@dash.route('/api/filename',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def filename(current_user):
    if request.method == "GET":
        try:
            if verifyactive(current_user)==True:
                cur = mysql.connection.cursor()
                x = cur.execute("SELECT name,Date,status,ServiceType FROM recentfiles WHERE fid = %s ORDER BY DATE DESC LIMIT 5",[current_user])
                if x>0:
                    result = cur.fetchall()
                    mysql.connection.commit()
                    cur.close()
                    return jsonify({'success':True,'result':result})
                return jsonify({'success':True,'result':'NULL'})
            return jsonify({'success':True,'result':'No Subscription'})
        except:
            return jsonify({'success':False})
    return jsonify({'success':False})

@dash.route('/api/subscription',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def subscription__details(current_user):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT service_name,subscription_type,ExpiryDate,time,status FROM SERVICES WHERE fid=%s AND status=%s",[current_user,"active"])
        result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'result': result})
    return jsonify({'success':False})

@dash.route('/api/usagekeywords',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def usagekeywords(current_user):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        x = cur.execute("SELECT Keywords,KeywordTotal FROM `usage` WHERE fid=%s AND WordCloud IS NULL",[current_user])
        if x>0:
            result = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            presentkeys = result.get('Keywords')
            if presentkeys == 0:
                innerkeywords(current_user)
            return jsonify({'success':True,'result':result})
        return jsonify({'success':True,'result':'NULL'})
    return jsonify({'success':False})

@dash.route('/api/usagewordcloud',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def usagewordcloud(current_user):
    if request.method == "GET":
        cur = mysql.connection.cursor()
        x =cur.execute("SELECT WordCloud,WordcloudTotal FROM `usage` WHERE fid=%s AND Keywords IS NULL",[current_user])
        if x>0:
            result = cur.fetchone()
            mysql.connection.commit()
            cur.close()
            return jsonify({'success':True,'result':result})
        return jsonify({'success':True,'result':'NULL'})
    return jsonify({'success':False})

@dash.route('/api/config_service',methods=['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def config_service(current_user):
    if request.method =='GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT service_name,purchaseDate,ExpiryDate,subscription_type,cost FROM SERVICES WHERE fid=%s AND status IN ('active','In-progress')",[current_user])
        result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return jsonify({"success":True,"result":result})
    return jsonify({"success":False})

# //////
@dash.route('/api/billing',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def Service(current_user):
    if request.method == "POST":
        fid = current_user
        payment_id = request.json['Payment_id']
        FullName = request.json['FullName']
        Email = request.json['Email']
        Mobile = request.json['Mobile']
        Country = request.json['Country']
        State = request.json['State']
        City = request.json['City']
        Zip_code = request.json['Zip_code']
        GST = request.json['GST']
        service_name = request.json['service_name']
        subscription_type = request.json['subscription_type']
        usage_value = request.json['usage_value']
        cost = request.json['cost']
        purchaseDate =request.json['purchaseDate']
        ExpiryDate = request.json['ExpiryDate']
        time = datetime.datetime.now()
        # integrating razor pay
        # razorpay(cost)
        # making integration then storing the data
        cur = mysql.connection.cursor()
        user_sub = cur.execute('SELECT service_name FROM `SERVICES` WHERE fid=%s AND status=%s',[current_user,"active"])
        print(user_sub)
        if user_sub == 2:
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO `SERVICES` (fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,"In-progress"])
            cur.execute('INSERT INTO `billing__details` (fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
            mysql.connection.commit()   
        elif user_sub > 0 :
            service = cur.fetchone()
            get_service_name = service.get('service_name')
            print("get_service_name",get_service_name)
            print("service_name",service_name)
            if get_service_name == "Keywords" and service_name == "Keywords":
                print("....key")
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO `SERVICES` (fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,"In-progress"])
                # cur.execute('INSERT INTO `billing__details` (fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
                cur.execute('INSERT INTO `billing__details` (fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
                mysql.connection.commit()
            if get_service_name == "WordCloud" and service_name == "WordCloud":
                print("....words")
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO `SERVICES` (fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,"In-progress"])
                # cur.execute('INSERT INTO `billing__details` (fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
                cur.execute('INSERT INTO `billing__details` (fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
                mysql.connection.commit()
            if get_service_name != service_name:
                print(".....,not equal")
                # cur.execute('INSERT INTO `billing__details` (fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
                cur.execute('INSERT INTO `billing__details` (fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
                cur.execute('INSERT INTO `SERVICES` (fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,"active"])
                mysql.connection.commit()
                if service_name == "Keywords":
                    cur.execute('INSERT INTO `usage` (fid,Keywords,KeywordTotal) values(%s,%s,%s)',[fid,usage_value,usage_value])
                    mysql.connection.commit()
                elif service_name == "WordCloud":
                    cur.execute('INSERT INTO `usage` (fid,WordCloud,WordcloudTotal) values(%s,%s,%s)',[fid,usage_value,usage_value])
                    mysql.connection.commit()
        else:
            # cur.execute('INSERT INTO `billing__details` (fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
            cur.execute('INSERT INTO `billing__details` (fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,payment_id,FullName,Email,Mobile,Country,State,City,Zip_code,GST])
            cur.execute('INSERT INTO `SERVICES` (fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',[fid,service_name,subscription_type,usage_value,cost,purchaseDate,ExpiryDate,time,"active"])
            mysql.connection.commit()
            if service_name == "Keywords":
                    cur.execute('INSERT INTO `usage` (fid,Keywords,KeywordTotal) values(%s,%s,%s)',[fid,usage_value,usage_value])
                    mysql.connection.commit()
            elif service_name == "WordCloud":
                cur.execute('INSERT INTO `usage` (fid,WordCloud,WordcloudTotal) values(%s,%s,%s)',[fid,usage_value,usage_value])
                mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'result': "sucess"})
    return jsonify({'success':False})

@dash.route('/api/billing_detils',methods=["GET"])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def billing_details(current_user):
    if request.method=="GET":
        pass