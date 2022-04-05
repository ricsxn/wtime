import json
import logging
import datetime
import time
import uuid
import smtplib
import socket
from flask import Flask, request, render_template, jsonify, make_response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user

app=Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = '1b3eb80ea0ffb1ac13ebe460438e057b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wtime_srv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BANNED_IPS']='banned_ips'

app_info = {
  'title': 'WTime Server',
  'author': 'Riccardo Bruno',
  'contact': 'riccardo.bruno@ct.infn.it',
  'company': 'INFN Dept. of Catania',
  'site_name': 'Catania',
  'site_url': 'https://juno-lab-01.ct.infn.it',
  'proxy_prefix': '',
  'mail_from': 'juno',
  'logfile': 'wtime_srv.log',
}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from wtime_srv_model import DB,\
                            User

logging.basicConfig(filename='wtime_srv.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
log=app.logger

#
# DB
#
@app.route('/setupdb')
def create_db():
    db = DB()
    db.create_db()
    if db.error != '':
      return jsonify(error='Could not create database: \'%s\'' % db.error, status=400)
    return jsonify(message='Database created', status=200)


#
# GUI
#

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user, page_title='WTime Home', app_info=app_info)


#
# APIs
#

def process_input(request, columns):
    input_data = {}
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
        for c in columns:
            if json.get(c, None) is not None:
                input_data[c] = json.get(c)
    else:
        for c in columns:
            if request.form.get('line', None) is not None:
                input_data[c] = request.form.get(c) 
    print('input_data', input_data)
    return input_data

#
# Users
#

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user_first_name = request.form.get('first_name','').strip()
        user_last_name = request.form.get('last_name','').strip()
        user_email = request.form.get('user_email','').strip()
        try:
            # Gemerate user_hash if needed
            u = find_user(user_email)
            if u is None:
                user_hash = "%s" % uuid.uuid4()
            else:
                user_hash = u.hash
            #  Send an email to the user containing the activation URL
            if (user_first_name is None or user_first_name == '') and\
               (user_last_name is None or user_last_name == ''):
                dear_user="wtime user"
            else:
                dear_user = user_first_name + " " + user_last_name
            activating_url = request.host_url + "go/%s?first_name=%s&last_name=%s&email=%s" % (user_hash, user_first_name, user_last_name, user_email)
            user_message = ("""To: %s\r\n"""
                            """Subject: WTime user activation\r\n\r\n"""
                            """Dear %s,\r\n\r\n"""
                            """Please activate your WTime service just clicking on the following link: %s\r\n\r\n"""
                            """Regards,\r\n"""
                            """WTime server\r\n""") % (
                user_email.strip(),
                dear_user,
                activating_url,
            )
            server = smtplib.SMTP('localhost')
            server.set_debuglevel(1)
            server.sendmail(app_info['mail_from'], user_email, user_message)
            server.quit()  
            return render_template('mail_sent.html', page_title='Wait for activation', app_info=app_info)
        except Exception as e:
            print("login exception: %s" % e)
    elif request.method == 'GET':
        return render_template('login.html', page_title='Login/Register', app_info=app_info)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    resp = make_response(render_template('logout.html', app_info=app_info))
    resp.set_cookie('user_hash', '', expires=0)
    return resp

@app.route('/user_info/')
@login_required
def user_info():
    return render_template('user_info.html', page_title='User info', app_info=app_info)

#
# User APIs
#
def find_user(email, hash=None):
    users = User.query.order_by(User.id).all()
    for u in users:
       if (email is not None and u.email == email) or\
          (hash is not None and u.hash == hash):
           print("User found!")
           return u
    return None


@app.route('/go/<user_hash>', methods=['GET', ])
def go(user_hash):
    first_name = request.args.get('first_name','')
    last_name = request.args.get('last_name','')
    email = request.args.get('email','')
    u = find_user(None, user_hash)
    if u is None:
        print("Creating user")
        u = User()
        u.firstname = first_name
        u.lastname = last_name
        u.hash = user_hash
        u.email = email
        db.session.add(u)
        db.session.commit()
    login_user(u)
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('user_hash', user_hash)
    return resp


# http://localhost:8889//go/94f2a311-230a-4beb-a791-f33266091169?first_name=Riccardo&last_name=Bruno&email=riccardo.bruno@ct.infn.it


#
# General
#

#def lock_forever():
#    while True:
#        time.sleep(3600) # block the request till client timeout
#
#def block_ip(block_ip):
#    bip_f = None
#    try:
#        bip_f = open(app.config['BANNED_IPS'],'a')
#        bip_f.write(block_ip + '\n')
#        print('Warning, blocked IP: \'%s\'' % block_ip)
#    except IOError as e:
#        print('Warning, not existing \'%s\' file', app.config['BANNED_IPS'])
#    finally:
#        if bip_f is not None:
#            bip_f.close()
#
#@app.before_request
#def block_method():
#    bip_f = None
#    bip_list = []
#    try:
#        bip_f = open(app.config['BANNED_IPS'],'r')
#        bip_list = []
#        while True:
#            ip = bip_f.readline()
#            if not ip:
#                break
#            bip_list += [ip.split('\n')[0], ]
#        bip_f.close()
#        req_ip = request.environ.get('REMOTE_ADDR')
#        if req_ip in bip_list:
#            return lock_forever()
#    except IOError as e:
#        print('Warning, not existing \'%s\' file', app.config['BANNED_IPS'])
#    finally:
#        if bip_f is not None:
#            bip_f.close()
#
#@app.errorhandler(404)
#def page_not_found(error):
#    req_ip = request.environ.get('REMOTE_ADDR')
#    block_ip(req_ip)
#    return lock_forever()
#
#@app.errorhandler(400)
#def bad_request(error):
#    req_ip = request.environ.get('REMOTE_ADDR')
#    block_ip(req_ip)
#    return lock_forever()
