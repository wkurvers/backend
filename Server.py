from flask_login import LoginManager, current_user, login_required, logout_user
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, make_response, session
import os
import UserApi, LoginForm, eventApi
import sys
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

import UserApi, LoginForm, eventApi,RegisterForm
import sys, string, os, random

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


################################################################
# login/logout
################################################################

#check if user is loggedin if not try to log user in.
# return 0/1 for counselor, true is for showing login or logout in menu.
@app.route('/login', methods=['POST'])
def loginPageHandler():
    if current_user.is_authenticated:
        return jsonify({'value': False, 'clearance': None, 'userId': None})
    else:
        user = LoginForm.loginUser(request.get_json())
        if(user != False):
            return jsonify({'value': True, 'clearance': user.clearance, 'userId': user.id})
        else:
            return jsonify({'value': False, 'clearance': None, 'userId': None})

# check if user is loggedin using current_user from flask.
@app.route('/api/loginCheck', methods=['GET'])
def loginCheck():
    if current_user.is_authenticated:
        return jsonify({"value": True, "email": current_user.email})
    else:
        return jsonify("value": False "email": None)

@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/reset-password', methods=['POST'])
def resetPassword():
    if(request.method == "POST"):
        data = json.loads(request.data)
        email = data['email']
        newPass = getNewPassword(email)

        # create message object instance
        msg = MIMEMultipart()

        message = "You're password has been reset. Your new password is: " + newPass + ". Please change you're password after you've logged in."

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

def getNewPassword(email, size=6, chars=string.ascii_uppercase + string.digits):
    email = email
    temp =  ''.join(random.choice(chars) for _ in range(size))
    UserApi.saveNewPassword(temp,email)
    return temp

@app.route('/api/changePassword', methods=['GET'])
def changePassword():
    newPassword = request.args.get('password',None)
    email = current_user.email
    return UserApi.changePassword(email,newPassword)

################################################################
# points and stampcard
################################################################

@app.route('/api/checkPoints', methods=['GET'])
def checkPoints():
    email = current_user.email
    return jsonify({"points": UserApi.checkPoints(email)})

@app.route('/api/addPoint', methods=['GET'])
def addPoint():
    email = current_user.email
    return jsonify({"responseCode": UserApi.addPoints(email)})

@app.route('/api/substractPoint', methods=['GET'])
def substractPoint():
    email = current_user.email
    return jsonify({"responseCode": UserApi.substractPoint(email)})

@app.route('/api/resetStampCard', methods=['GET'])
def resetStampCard():
    email = current_user.email
    return jsonify({"responseCode": UserApi.resetStampCard(email)})

################################################################
# events
################################################################

@app.route('/api/createEvent', methods=['POST'])
def createEvent():
    data = request.get_json()
    return jsonify({"responseCode": eventApi.createEvent(data.get("id"),
                                    data.get('name'),
                                    data.get('begin'),
                                    data.get('end'),
                                    data.get('location'),
                                    data.get('description'),
                                    data.get('leader'),
                                    data.get('img'))})

################################################################
# news
################################################################

@app.route('/api/createNews', methods=['POST'])
def createNews(emtpy):
    return None

################################################################
# miscellaneous
################################################################

@app.route('/api/qrEvent', methods=['POST'])
def eventScanned():
    data = request.get_json()
    eventId = data.get('eventId')
    personId = data.get('personId')
    if eventApi.isScanned(eventId, personId):
        return jsonify({"responseCode": "400"})
    else:
        responseCode = eventApi.eventScanned(eventId,personId)
        return jsonify({"responseCode": responseCode})

@app.route('/api/eventByCode', methods=['POST'])
def findEvent():
    data = request.get_json()
    qrCode = data.get("qrCode")
    result = eventApi.findEvent(qrCode)
    if result:
        return jsonify({"responseCode": "200", "eventId": result.id})
    return jsonify({"responseCode": "400", "eventId": None})


@app.route('/register', methods=['POST'])
def registerHandler():
    return jsonify(RegisterForm.registerSubmit(request.get_json()))


if __name__ == "__main__":
    app.run(debug=True)
