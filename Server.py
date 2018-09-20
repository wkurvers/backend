from flask_login import LoginManager, current_user, login_required, logout_user
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, make_response, session
import os
#import UserApi, LoginForm, eventApi
import sys
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json


app = Flask(__name__)
app.secret_key = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

# function for flask_login
@login_manager.user_loader
def load_user(person_id):
    return UserApi.getPerson(person_id)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
    return render_template('index.html')

#check if user is loggedin if not try to log user in.
# return 0/1 for counselor, true is for showing login or logout in menu.
@app.route('/login', methods=['POST'])
def loginPageHandler():
    if current_user.is_authenticated:
        return 400
    else:
        return jsonify({'value': True, 'clearance': current_user.clearance}),LoginForm.loginUser(request.args)

# check if user is loggedin using current_user from flask.
@app.route('/api/loginCheck', methods=['GET'])
def loginCheck():
    check = current_user.is_authenticated
    if check:
        print(current_user.username, file=sys.stderr)
        return jsonify({"username": current_user.username})
    else:
        return jsonify(False)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/api/qrEvent', methods=['GET'])
def eventScanned():
    eventId = request.args.get('eventId', None)
    personId = request.args.get('personId', None)
    if eventApi.isScanned(eventId, personId):
        return jsonify(False)
    else:
        return eventApi.eventScanned(eventId,personId)

@app.route('/reset-password', methods=['POST'])
def resetPassword():
	if(request.method == "POST"):
		data = json.loads(request.data)
		email = data['email']

		# create message object instance
		msg = MIMEMultipart()


		message = "You're password has been reset. Your new password is: <ww>. Please change you're password after you've loggedin."

		# setup the parameters of the message
		msg['From'] = "bslim@grombouts.nl"
		msg['To'] = email
		msg['Subject'] = "Password reset"

		# add in the message body
		msg.attach(MIMEText(message, 'plain'))

		# Send the message via our own SMTP server.
		server = smtplib.SMTP('mail.grombouts.nl', 587)
		server.starttls()
		server.login('bslim@grombouts.nl', "bslim")
		server.sendmail('bslim@grombouts.nl', email,  msg.as_string())
		server.quit()

	return " "
