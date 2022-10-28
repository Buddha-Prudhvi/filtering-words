from ast import Break
from datetime import datetime
from flask import Flask,Blueprint,request,jsonify,session
from flask_mysqldb import MySQL
from itsdangerous import base64_decode
from flask_cors import cross_origin
import textract
from nltk.tokenize import  sent_tokenize, word_tokenize 
from nltk.corpus import stopwords
import base64
import os
from werkzeug.utils import secure_filename
from auth import token_required,innerkeywords
from datetime import date

app = Flask(__name__)
service = Blueprint('service', __name__)

mysql = MySQL(app)

save_path = '/home/prudhvib/Desktop/GCS_APP/gcs---backend/files'

"""file upload with keywords"""
@service.route('/api/fileupload',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def filename(current_user):
    if request.method == "POST":
        cur = mysql.connection.cursor()
        subscribed = cur.execute('SELECT Keywords FROM `usage` WHERE fid=%s AND KeywordTotal IS NOT NULL',[current_user])
        usage = cur.fetchone()
        mysql.connection.commit()
        if subscribed == 0:
            return jsonify({'success':True,'message':"no subscription"})
        else:
            keywords_now = usage.get('Keywords')
            if keywords_now == 0:
                innerkeywords(current_user)
                return jsonify({"success":True,"message":"please check subscription before continue the service"})
            if keywords_now > 0:
                file = request.files['file']
                custom_words = request.form.get('custom_words')
                filename = file.filename
                readfile = file.read()
                encode_data = base64.b64encode(readfile)
                encode_data_string = encode_data.decode('utf-8')
                decode_file = base64.decodebytes(encode_data)
                files_file = os.path.join(save_path,filename)
                f = open(files_file,'wb')
                f.write(decode_file)
                f.close()
                filepath = save_path+'/'+filename
                custom = list(custom_words.lower().split(","))
                extension = filename.split(".")[-1]
                file_textract = textract.process(filepath)
                file_Data = file_textract.decode('utf-8')
                total_words = word_tokenize(file_Data)
                new_words = [w.lower() for w in total_words if w.isalpha()]
                no_stop_words = []
                filtered_words = []
                cst_idf = {}
                for e_word in new_words:
                    if e_word  not in stopwords.words('english'):
                        no_stop_words.append(e_word)
                for w in no_stop_words:
                    if w in custom:
                        filtered_words.append(w)
                        if w in cst_idf:
                            cst_idf[w] = cst_idf[w]+1
                        else:
                            cst_idf[w] = 1
                filter_words = list(set(filtered_words))
                if len(filtered_words) == 0:
                    filter_words = "no keywords found"
                Date = datetime.now()
                cur.execute("INSERT INTO upload_files(fid,name,file,filepath,extension,output,Date,ServiceType,Status,Keywords) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[current_user,filename,encode_data_string,filepath,extension,cst_idf,Date,"keywords","success",str(filter_words)])
                mysql.connection.commit()
                update_keywords = keywords_now-1
                cur.execute("UPDATE `usage` SET Keywords=%s WHERE fid=%s AND KeywordTotal IS NOT NULL",(update_keywords,current_user))
                mysql.connection.commit()
                cur.close()
                return jsonify({'success':True,'message':filter_words,'repeatedwords':filtered_words,'idf':cst_idf})
            return jsonify({'success':False})

"""custom file upload """
@service.route('/api/customfileupload',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def customfile(current_user):
    if request.method=="POST":
        try:
            custom_file = request.files['custom_file']
            readfile = custom_file.read()
            encode_data = base64.b64encode(readfile)
            cur = mysql.connection.cursor()
            res = cur.execute("SELECT custom_file FROM custom_file WHERE fid = %s",[current_user['_id']])
            if res>0:
                cur.execute("UPDATE custom_file SET custom_file =%s WHERE fid = %s",[encode_data,current_user['_id']])
            else:
                cur.execute("INSERT INTO custom_file(fid,custom_file) VALUES(%s,%s)",[current_user['_id'],encode_data])
            mysql.connection.commit()
            cur.close()
            return jsonify({'success':True,'message':'successfully uploaded'})
        except:
            return jsonify({"sucess":False,'message':"upload failed"})
            
"""extaraction of keywords by custom_file"""
@service.route('/api/custom_upload',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def custom_upload(current_user):
    if request.method == "POST":
        try:
            file = request.files['file']
            fid = current_user
            cur = mysql.connection.cursor()
            cur.execute("SELECT custom_file FROM custom_file where fid = %s",[current_user['_id']])
            mysql.connection.commit()
            custom_file = cur.fetchone()
            cur.close()
            decodecust_file = base64.decodebytes(custom_file['custom_file'])
            filename = file.filename
            readfile = file.read()
            encode_data = base64.b64encode(readfile)
            decode_file = base64.decodebytes(encode_data)
            files_file = os.path.join(save_path,filename)
            f = open(files_file,'wb')
            f.write(decode_file)
            f.close()
            filepath = save_path+'/'+filename
            x = decodecust_file.decode('utf-8')
            custom = x
            extension = filename.split(".")[-1]
            file_textract = textract.process(filepath)
            file_Data = file_textract.decode('utf-8')
            total_words = word_tokenize(file_Data)
            new_words = [w.lower() for w in total_words if w.isalpha()]
            no_stop_words = []
            filtered_words = []
            cst_idf = {}
            for e_word in new_words:
                if e_word  not in stopwords.words('english'):
                    no_stop_words.append(e_word)
            for w in no_stop_words:
                if w in custom:
                    filtered_words.append(w)
                    if w in cst_idf:
                        cst_idf[w] = cst_idf[w]+1
                    else:
                        cst_idf[w] = 1
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO upload_files(fid,name,file,extension,output) VALUES(%s,%s,%s,%s,%s)",[fid,filename,encode_data,extension,cst_idf])
            mysql.connection.commit()
            cur.close()
            return jsonify({'success':True,'message':filtered_words,'idf':cst_idf})
        except:
            return jsonify({'success':False})
