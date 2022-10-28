
from uuid import UUID
from flask import Blueprint, request, session, jsonify,Flask
from functools import wraps
from flask_mysqldb import MySQL
import jwt
from datetime import date

app = Flask(__name__)
mysql = MySQL(app)

def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token: 
            return jsonify({'message':'Token is missing'}),401
        try:
            data = jwt.decode(token,str(app.config['SECRET_KEY']),algorithms=['HS256'])
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM REGISTER_DETAIL WHERE UUId = %s",[data['public_id']])
            data = cur.fetchone()
            current_user = data['id']
            mysql.connection.commit()
            cur.close()
        except:
            return jsonify({'message':'Token is invalid'}),401
        return f(current_user,*args,**kwargs)
    return decorated


def innerkeywords(current_user):
    try:
        cur = mysql.connection.cursor()
        users = cur.execute('SELECT * from `SERVICES` WHERE fid=%s AND status=%s AND service_name=%s',[current_user,"In-progress","Keywords"])
        if users>0:
            cur.execute('UPDATE `SERVICES` SET status=%s WHERE  fid=%s AND status=%s AND service_name=%s',("DeActivated",current_user,"active","Keywords"))
            x = cur.execute('DELETE FROM `usage` WHERE  fid=%s AND WordCloud IS NULL',[current_user])
            uses = cur.execute('SELECT MIN(time) from `SERVICES` WHERE fid=%s AND status=%s AND service_name=%s',[current_user,"In-progress","Keywords"])
            if uses > 0:
                x = cur.fetchone()
                mysql.connection.commit()
                min_pur_date = x.get('MIN(time)')
                p = cur.execute('UPDATE `SERVICES` SET status=%s WHERE fid=%s AND time=%s AND service_name=%s AND status=%s',("active",current_user,min_pur_date,"Keywords","In-progress"))
                mysql.connection.commit()
                a = cur.execute("SELECT * FROM `SERVICES` WHERE fid=%s AND status=%s AND service_name=%s",[current_user,"active","Keywords"])
                new_active = cur.fetchone()
                mysql.connection.commit()
                usage_value = new_active.get('usage_value')
                cur.execute('INSERT INTO `usage` (fid,Keywords,KeywordTotal) VALUES(%s,%s,%s)',[current_user,usage_value,usage_value])
                mysql.connection.commit()
                # filename()
                return jsonify({"success":True,"message":"subscription updated please continue the service"})
            return jsonify({"success":True,"message":"please subscribe to continue the service"}) 
    except TypeError as te:
        return jsonify({"message":"subscription"})



def innerwords(current_user):
    try:
        cur = mysql.connection.cursor()
        users = cur.execute('SELECT * from `SERVICES` WHERE fid=%s AND status=%s AND service_name=%s',[current_user,"In-progress","WordCloud"])
        if users>0:
            cur.execute('UPDATE `SERVICES` SET status=%s WHERE  fid=%s AND status=%s AND service_name=%s',("DeActivated",current_user,"active","WordCloud"))
            x = cur.execute('DELETE FROM `usage` WHERE  fid=%s AND Keywords IS NULL',[current_user])
            uses = cur.execute('SELECT MIN(time) from `SERVICES` WHERE fid=%s AND status=%s AND service_name=%s',[current_user,"In-progress","WordCloud"])
            if uses > 0:
                x = cur.fetchone()
                mysql.connection.commit()
                min_pur_date = x.get('MIN(time)')
                p = cur.execute('UPDATE `SERVICES` SET status=%s WHERE fid=%s AND time=%s AND service_name=%s AND status=%s',("active",current_user,min_pur_date,"WordCloud","In-progress"))
                mysql.connection.commit()
                a = cur.execute("SELECT * FROM `SERVICES` WHERE fid=%s AND status=%s AND service_name=%s",[current_user,"active","WordCloud"])
                new_active = cur.fetchone()
                mysql.connection.commit()
                usage_value = new_active.get('usage_value')
                cur.execute('INSERT INTO `usage` (fid,WordCloud,WordcloudTotal) VALUES(%s,%s,%s)',[current_user,usage_value,usage_value])
                mysql.connection.commit()
                # filename()
                return jsonify({"success":True,"message":"subscription updated please continue the service"})
            return jsonify({"success":True,"message":"please subscribe to continue the service"}) 
    except TypeError as te:
        return jsonify({"message":"subscription"})

def verifyactive(current_user):
    cur = mysql.connection.cursor()
    active_user = cur.execute('SELECT * FROM `SERVICES` WHERE fid=%s AND status=%s',[current_user,"active"])
    if active_user >0:
        return True
    return False