from flask import Flask,Blueprint,request,jsonify,session
from flask_mysqldb import MySQL
from flask_cors import cross_origin
import datetime

app = Flask(__name__)
dash = Blueprint('dash', __name__)

mysql = MySQL(app)

@dash.route('/api/filename',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def filename():
    if request.method == "POST":
        try:
            Filename = request.json['Filename']
            ServiceType = request.json['ServiceType']
            # PreviewLink = "https://file-examples-com.github.io/uploads/2017/10/file-example_PDF_500_kB.pdf"
            PreviewLink = "./files/"
            Date = datetime.datetime.now().date()
            Status = request.json['Status']
            Download = "https://file-examples-com.github.io/uploads/2017/10/file-example_PDF_500_kB.pdf"
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO RECENT_FILES(Filename,ServiceType,PreviewLink,Date,Status,Download) VALUES(%s,%s,%s,%s,%s,%s)",[Filename,ServiceType,PreviewLink,Date,Status,Download])
            mysql.connection.commit()
            cur.close()
            return jsonify({'success': True, 'result': "sucess"})
        except:
            return jsonify ({'success':False})
    if request.method == "GET":
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM RECENT_FILES ")
            result = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            return jsonify({'success':True,'result':result})
        except:
            return jsonify({'success':False})
    return jsonify({'success':False})

@dash.route('/api/subscription',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def subscription__details():
    if request.method == "POST":
        ProductName = request.json['ProductName']
        Subscription = request.json['Subscription']
        ExpiryDate = request.json['ExpiryDate']
        Status = request.json['Status']
        RemainingDays = request.json['RemainingDays']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO subscription__details(FID,ProductName,Subscriptions,ExpiryDate,Status,RemainingDays) VALUES(%s,%s,%s,%s,%s,%s)",[session.get('id'),ProductName,Subscription,ExpiryDate,Status,RemainingDays])
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'result': "sucess"})
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM subscription__details")
        result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return jsonify({'success':True,'result':result})
    return jsonify({'success':False})

@dash.route('/api/usage',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def usage():
    if request.method == "POST":
        keyWords = request.json['keywords']
        keywordTotal = request.json['keywordTotal']
        WordCloudUsage = request.json['WordCloudUsage']
        WordcloudTotal = request.json[' ']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO `usage` (keywords,keywordTotal,WordCloudUsage,WordcloudTotal) VALUES(%s,%s,%s,%s)",[keyWords,keywordTotal,WordCloudUsage,WordcloudTotal])
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'result': "sucess"})
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `usage`")
        result = cur.fetchall()
        mysql.connection.commit()
        cur.close()
        return jsonify({'success':True,'result':result})
    return jsonify({'success':False})