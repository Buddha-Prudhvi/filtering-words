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
import numpy as np

app = Flask(__name__)
service = Blueprint('service', __name__)

mysql = MySQL(app)

save_path = '/home/prudhvib/Desktop/GCS_APP/gcs---backend/files'

@service.route('/api/fileupload',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def filename():
    if request.method == "POST":
        # try:
            file = request.files['file']
            filename = file.filename
            readfile = file.read()
            encode_data = base64.b64encode(readfile)
            decode_file = base64.decodebytes(encode_data)
            files_file = os.path.join(save_path,filename)
            f = open(files_file,'wb')
            f.write(decode_file)
            f.close()
            filepath = save_path+'/'+filename
            custom_words = request.form.get('custom_words')
            fid = request.form.get('fid')
            bytes_fid = fid.encode('ascii')
            decode_fid = base64.b64decode(bytes_fid)
            fid_x = decode_fid.decode('utf-8')
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
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO upload_files(fid,name,file,extension,output,Date,ServiceType,Status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",[fid_x,filename,encode_data,extension,cst_idf,Date,"keywords","success"])
            mysql.connection.commit()
            cur.close()
            return jsonify({'success':True,'message':filter_words,'idf':cst_idf})
        # except:
        #     return jsonify({'success':False})

@service.route('/api/customfileupload',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def customfile():
    if request.method=="POST":
        try:
            custom_file = request.files['custom_file']
            fid = request.form.get('fid')
            readfile = custom_file.read()
            encode_data = base64.b64encode(readfile)
            cur = mysql.connection.cursor()
            res = cur.execute("SELECT custom_file FROM custom_file WHERE fid = %s",[fid])
            if res>0:
                cur.execute("UPDATE custom_file SET custom_file =%s WHERE fid = %s",[encode_data,fid])
            else:
                cur.execute("INSERT INTO custom_file(fid,custom_file) VALUES(%s,%s)",[fid,encode_data])
            mysql.connection.commit()
            cur.close()
            return jsonify({'success':True,'message':'successfully uploaded'})
        except:
            return jsonify({"sucess":False,'message':"upload failed"})
    
@service.route('/api/custom_upload',methods = ['POST','GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def custom_upload():
    if request.method == "POST":
        try:
            file = request.files['file']
            fid = request.form.get('fid')
            cur = mysql.connection.cursor()
            cur.execute("SELECT custom_file FROM custom_file where fid = %s",[fid])
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