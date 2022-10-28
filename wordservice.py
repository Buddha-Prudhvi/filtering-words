from cgi import test
from email.mime import image
from flask import Blueprint, request, session, jsonify,Flask
from flask_cors import cross_origin
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from flask_mysqldb import MySQL
from nltk.tokenize import  sent_tokenize, word_tokenize 
import re
from auth import token_required
import uuid
import base64 
from json import dumps
from base64 import b64encode
import os
import textract
from nltk.tokenize import  sent_tokenize, word_tokenize 
from nltk.corpus import stopwords
from datetime import datetime
from auth import innerwords

app = Flask(__name__)
cloudservice = Blueprint('cloudservice', __name__)
mysql = MySQL(app)

save_path = '/home/prudhvib/Desktop/GCS_APP/gcs---backend/images'
image_path ='/home/prudhvib/Desktop/GCS_APP/gcs---backend/word_images'


@cloudservice.route('/api/wordcloudkeys',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def cloud_image_keys(current_user):
    if request.method == "POST":
        # hjhdfj
        cur = mysql.connection.cursor()
        subscribed = cur.execute('SELECT WordCloud FROM `usage` WHERE fid=%s AND WordcloudTotal IS NOT NULL',[current_user])
        if subscribed == 0:
            return jsonify({'success':True,'message':"no subscription"})
        else:
            usage = cur.fetchone()
            print("usage",usage)
            wordscloud_now = usage.get('WordCloud')
            if wordscloud_now == 0:
                innerwords(current_user)
                return jsonify({"success":True,"message":"please check subscription before continue the service"})
            if wordscloud_now > 0:
                words = request.json['keywords']
                UUID = str(uuid.uuid4())
                words_str = str(words)
                text_string = re.sub(r"[\['\]\s]", "", words_str)
                words_counter = Counter(text_string.split(','))
                custom_mask = np.array(Image.open(save_path+"/cloudd.jpg"))
                wc = WordCloud(background_color="white", mask=custom_mask,contour_width=1)
                wc.generate_from_frequencies(words_counter)
                imagep = image_path+"/"+UUID+".png"
                wc.to_file(imagep)
                update_words = wordscloud_now -1
                cur.execute("UPDATE `usage` SET WordCloud=%s WHERE fid=%s AND WordcloudTotal IS NOT NULL",(update_words,current_user))
                mysql.connection.commit()
                cur.close()
                img = open(imagep,'rb').read()
                img_bytes = b64encode(img)
                imag = img_bytes.decode('utf-8')
                return jsonify({"result":"success","image":imagep,"img":imag})
        return jsonify({"result":"fail"})

"""generating wordcloud with keywords"""
@cloudservice.route('/api/wordcloud',methods=['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
@token_required
def cloud_image(current_user):
    if request.method == "POST":
        cur = mysql.connection.cursor()
        subscribed = cur.execute('SELECT WordCloud FROM `usage` WHERE fid=%s AND WordcloudTotal IS NOT NULL',[current_user])
        if subscribed == 0:
            return jsonify({'success':True,'message':"no subscription"})
        else:
            usage = cur.fetchone()
            mysql.connection.commit()
            wordscloud_now = usage.get('WordCloud')
            if wordscloud_now == 0:
                innerwords(current_user)
                return jsonify({"success":True,"message":"please check subscription before continue the service"})
            if wordscloud_now > 0:
                file = request.files['file']
                custom_words = request.form.get('custom_words')
                filename = file.filename
                readfile = file.read()
                encode_data = base64.b64encode(readfile)
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
                # cst_idf = {}
                for e_word in new_words:
                    if e_word  not in stopwords.words('english'):
                        no_stop_words.append(e_word)
                for w in no_stop_words:
                    if w in custom:
                        filtered_words.append(w)
                filter_words = list(set(filtered_words))
                print(filtered_words)
                if len(filtered_words) == 0:
                    return jsonify({"success":True,"filterwords":"no keywords found"})
                Date = datetime.now()
                UUID = str(uuid.uuid4())
                words = str(filtered_words)
                text_string = re.sub(r"[\['\]\s]", "",words)
                words_counter = Counter(text_string.split(','))
                custom_mask = np.array(Image.open(save_path+"/cloudd.jpg"))
                wc = WordCloud(background_color="white", mask=custom_mask,contour_width=1)
                wc.generate_from_frequencies(words_counter)
                imagep = image_path+"/"+UUID+".png"
                wc.to_file(imagep)
                cur.execute("INSERT INTO upload_word_files(fid,file_name,file,file_path,extension,Date,image_path,Status,ServiceType,Keywords) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[current_user,filename,encode_data,filepath,extension,Date,imagep,"success","Word Cloud",str(filter_words)])
                mysql.connection.commit()
                update_keywords = wordscloud_now-1
                cur.execute("UPDATE `usage` SET WordCloud=%s WHERE fid=%s AND WordcloudTotal IS NOT NULL",(update_keywords,current_user))
                mysql.connection.commit()
                cur.close()
                img = open(imagep,'rb').read()
                img_bytes = b64encode(img)
                imag = img_bytes.decode('utf-8')
                return jsonify({"success":True,"image":imagep,"filterwords":filter_words,"img":imag})
        return jsonify({"success":False})