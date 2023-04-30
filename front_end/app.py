"""
Project: Kintsugi

Enter text to predict depression
"""

#Import all required Packages
import pandas as pd
import numpy as np
import pickle
from flask import Flask, request,render_template
import string
import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import mysql.connector as mysql
from templates.pythonFiles import contentbased
from templates.pythonFiles import learningToRank


#Intialize Flask application
app = Flask(__name__)
templates_dir = os.path.join(app.root_path, 'templates')


app.secret_key = 'super secret key' 
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Recommendation_system'
mysql = MySQL(app)

@app.route('/')
#Home page for the Application
def home():
    return render_template('home.html')

#Route for prediction template
@app.route('/prediction')
def prediction():
    return render_template('content_based.html')


#Route for login template
@app.route('/login',methods=['GET','POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM User_password WHERE userID = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['userID']
            session['password'] = account['password']
            msg = 'Logged in successfully !'

            content_list = contentbased.prediction(account['userID'])
            ltr_list = learningToRank.predict(account['userID'])

            msg1 = content_list

            # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
            # cur.execute("""SELECT * FROM useritem WHERE asin in item_suggest[:10]""")
            # user = cur.fetchone()
            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)           
            cursor1.execute('SELECT * FROM ItemDetails1 WHERE asin in (% s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ', (content_list[0],content_list[1],content_list[2],content_list[3],content_list[4],content_list[5],content_list[6],content_list[7],content_list[8],content_list[9]))
            item_details_c = cursor1.fetchall()
            #msg3 = type(item_details)
            item_details_content = []
            for i in range(0,len(item_details_c)) : 
                dict_temp = item_details_c[i]
                if [dict_temp['asin'],dict_temp['title'],dict_temp['brand'],dict_temp['price']] not in item_details_content : 
                    item_details_content.append([dict_temp['asin'],dict_temp['title'],dict_temp['brand'],dict_temp['price']])

            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)           
            cursor1.execute('SELECT * FROM ItemDetails1 WHERE asin in (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ', (ltr_list[0],ltr_list[1],ltr_list[2],ltr_list[3],ltr_list[4],ltr_list[5],ltr_list[6],ltr_list[7],ltr_list[8],ltr_list[9]))
            item_details_l = cursor1.fetchall()
            item_details_ltr = []
            for i in range(0,len(item_details_l)) : 
                dict_temp = item_details_l[i]
                if [dict_temp['asin'],dict_temp['title'],dict_temp['brand'],dict_temp['price']] not in item_details_ltr : 
                    item_details_ltr.append([dict_temp['asin'],dict_temp['title'],dict_temp['brand'],dict_temp['price']])


            return render_template('content_based.html',msg1 = content_list,msg2 = ltr_list,msg3 = item_details_content,msg4 = item_details_ltr)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)


#Route for Data Preview of Working Model
@app.route('/data_preview',methods=['POST'])
def data_preview():
    return render_template('data_preview.html')
    
#Route for html data table template
@app.route('/data')
def data():
    return render_template('data.html')

# Clear Browser Cache
def before_request():
    app.jinja_env.cache = {}


if __name__=='__main__':
    app.before_request(before_request)
    app.run()