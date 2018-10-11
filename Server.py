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

from bs4 import BeautifulSoup as BSHTML

import UserApi, LoginForm, eventApi, RegisterForm
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



@app.route('/api/createEventTrigger', methods=['GET'])
def createEventTrigger():
    data = requests.get("http://gromdroid.nl/bslim/wp-json/wp/v2/events/"+request.args.get("id")).json()
    soup = BSHTML(data["content"]["rendered"])
    images = soup.findAll('img')
    img = " "
    for image in images:
        img = image['src']
        print(image['src'])

    return jsonify({"responseCode": eventApi.createEvent(data["title"]["rendered"],
                                                         data["start"],
                                                         data["end"],
                                                         'Peizerweg 48',
                                                         data["content"]["rendered"],
                                                         '1',
                                                         img)})

################################################################
# login/logout
################################################################

# check if user is loggedin if not try to log user in.
# return 0/1 for counselor, true is for showing login or logout in menu.
@app.route('/login', methods=['POST'])
def loginPageHandler():
    if current_user.is_authenticated:
        return jsonify({'value': False, 'clearance': None, 'userId': None, "msg": "U bent al ingelogd"})
    else:
        response = LoginForm.loginUser(request.get_json())
        if response['boolean'] == "true":
            return jsonify(response)
        else:
            return jsonify(response)


# check if user is loggedin using current_user from flask.
@app.route('/api/loginCheck', methods=['POST'])
def loginCheck():
    return LoginForm.loginCheck(request.get_json())


@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    return jsonify({"value": LoginForm.logoutUser(data)})

@app.route('/changeEmailRequest', methods=['POST'])
def changeMail():
    data = request.get_json()
    oldEmail = data.get('oldEmail')
    if UserApi.getEmail(oldEmail) == None:
        return jsonify({'responseCode': 400, 'msg': "Email is not recognized"})
    user = UserApi.getUserByEmail(oldEmail)
    if UserApi.changeEmail(user.id) == 200:
        msg = MIMEMultipart()

        user = UserApi.getUserByEmail(oldEmail)
        message = "Om je e-mail adres te veranderen is er een veiligheids code gegenereerd: " + user.securityCode + ". Vul deze code in de app in en voer u nieuwe e-mail adres in."

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = oldEmail
        msg['Subject'] = "E-mail veranderen"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', oldEmail, msg.as_string())
        server.quit()
        return jsonify({'responseCode': 200, 'msg': 'Security code generated for ' + oldEmail, 'oldEmail': oldEmail})
    return jsonify({'responseCode': 500, 'msg': 'Could not generate security code'})

@app.route('/changeUserEmail', methods=['POST'])
def changeUserEmail():
    data = request.get_json()
    oldEmail = data.get('oldEmail')
    newEmail = data.get('newEmail')
    secCode = data.get('secCode')
    if not UserApi.checkSecCode(oldEmail,secCode):
        return jsonify({'responseCode': 400, 'msg': "Veiligheidscode is ongeldig."})
    if UserApi.changeUserEmail(oldEmail, newEmail) == 200:
        msg = MIMEMultipart()

        user = UserApi.getUserByEmail(newEmail)
        message = "Uw e-mail adres is succesvol verandert."

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = newEmail
        msg['Subject'] = "E-mail adres verandert"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', newEmail, msg.as_string())
        server.quit()
        return jsonify({'responseCode': 200, 'msg': 'Succesfuly changed e-mail address to ' + newEmail})
    return jsonify({'responseCode': 500, 'msg': 'Could not change e-mail address'})

@app.route('/reset-password', methods=['POST'])
def resetPassword():
    if (request.method == "POST"):
        data = json.loads(request.data)
        email = data['email']
        if (UserApi.getEmail(email) == None):
            return jsonify({"boolean": "false"})
        newPass = getNewPassword(email)

        # create message object instance
        msg = MIMEMultipart()

        message = "Je wachtwoord is gereset. Je nieuwe wachtwoord is " + newPass + ". Verander u wachtwoord zo snel mogelijk aub."

        # setup the parameters of the message
        msg['From'] = "bslim@grombouts.nl"
        msg['To'] = email
        msg['Subject'] = "Wachtwoord reset"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # Send the message via our own SMTP server.
        server = smtplib.SMTP('mail.grombouts.nl', 587)
        server.starttls()
        server.login('bslim@grombouts.nl', "bslim")
        server.sendmail('bslim@grombouts.nl', email, msg.as_string())
        server.quit()
    return " "


def getNewPassword(email, size=6, chars=string.ascii_uppercase + string.digits):
    email = email
    temp = ''.join(random.choice(chars) for _ in range(size))
    UserApi.saveNewPassword(temp, email)
    return temp


@app.route('/api/changePassword', methods=['POST'])
def changePassword():
    data = request.get_json()
    id = data.get('id')
    oldPassword = data.get('oldPassword')
    newPassword = data.get('newPassword')
    return jsonify({"responseCode": UserApi.changePassword(id, oldPassword, newPassword)})


################################################################
# points and stampcard
################################################################

@app.route('/api/checkPoints', methods=['POST'])
def checkPoints():
    data = request.get_json()
    return jsonify({"points": UserApi.checkPoints(data.get('id'))})


@app.route('/api/addPoint', methods=['POST'])
def addPoint():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.addPoints(data.get(id))})


@app.route('/api/substractPoint', methods=['POST'])
def substractPoint():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.substractPoint(data.get(id))})


@app.route('/api/resetStampCard', methods=['POST'])
def resetStampCard():
    data = request.get_json()
    return jsonify({"responseCode": UserApi.resetStampCard(data.get(id))})


################################################################
# events
################################################################

@app.route('/api/createEvent', methods=['POST'])
def createEvent():
    data = request.get_json()

    print(data)
    return jsonify({"responseCode": eventApi.createEvent(data.get('name'),
                                                         data.get('begin'),
                                                         data.get('end'),
                                                         data.get('location'),
                                                         data.get('description'),
                                                         data.get('leader'),
                                                         data.get('img'))})


@app.route('/api/subToEvent', methods=['POST'])
def subToEvent():
    data = request.get_json()
    return jsonify(eventApi.subToEvent(data.get("eventId"), data.get("personId")))

  
@app.route('/api/saveMedia', methods=['POST'])
def saveMedia():
    data = request.get_json()
    return eventApi.saveMedia(data.get("url"), data.get("eventName"))

@app.route('/api/searchEvent', methods=['POST'])
def searchEvent():
    data = request.get_json()
    result = eventApi.searchEvent(data.get("searchString"))
    if len(result) > 0:
        return jsonify({"responseCode": 200, "events": result})
    return jsonify({"responseCode": 400, "events": {} })


################################################################
# news
################################################################

@app.route('/api/createNewsItem', methods=['POST'])
def createNewsItem():
    data = request.get_json()

    print(data)
    return jsonify({"responseCode": UserApi.createNewsItem(data.get('title'),
                                                         data.get('content'),
                                                         data.get('img'))})


@app.route('/api/searchNews', methods=['POST'])
def searchNews():
    data = request.get_json()
    result = eventApi.searchNews(data.get("searchString"))
    if len(result) > 0:
        return jsonify({"responseCode": 200, "news": result})
    return jsonify({"responseCode": 400, "news": {} })

################################################################
# mentor
################################################################

@app.route('/api/addProfilePhoto', methods=['POST'])
def addProfilePhoto():
    data = request.get_json()
    return UserApi.addProfilePhoto(data.get('url'), data.get('id'))


@app.route('/api/getProfilePhoto', methods=['POST'])
def getProfilePhoto():
    data = request.get_json()
    return UserApi.getProfilePhoto(data.get('id'))


################################################################
# miscellaneous
################################################################

# Is called to add points to the user account when an event is scannend
@app.route('/api/qrEvent', methods=['POST'])
def eventScanned():
    data = request.get_json()
    eventId = data.get('eventId')
    personId = data.get('personId')
    if eventApi.isScanned(eventId, personId) == 400:
        return jsonify({"responseCode": "400"})
    else:
        responseCode = eventApi.eventScanned(eventId, personId)
        return jsonify({"responseCode": responseCode})


# Is called to get the id from an event when giving a qrCode, returns 200 when succesfull and 400 when not
@app.route('/api/eventByCode', methods=['POST'])
def findEvent():
    data = request.get_json()
    qrCode = data.get("qrCode")
    result = eventApi.findEvent(qrCode)
    if result:
        return jsonify({"responseCode": "200", "eventId": result.id})
    return jsonify({"responseCode": "400", "eventId": None})


# Is called to register a new user
@app.route('/register', methods=['POST'])
def registerNormalUser():
    return jsonify({"responseCode": RegisterForm.registerSubmit(request.get_json(), 0)})


# Is called to register a new admin
@app.route('/register-admin', methods=['POST'])
def registerAdmin():
    return jsonify({"responseCode": RegisterForm.registerSubmit(request.get_json(), 1)})

@app.route('/api/getAllEvents', methods=['POST'])
def getEvents():
    result = eventApi.getAllEvents()
    if len(result) > 0:
        return jsonify({"responseCode": 200, "events": result})
    return jsonify({"responseCode": 400, "events": {} })


@app.route('/api/getAllAdmins', methods=['POST'])
def getAdmins():
    result = UserApi.getAllAdmins()
    print(result)
    if len(result) > 0:
        return jsonify({"responseCode": 200, "admins": result})
    return jsonify({"responseCode": 400, "admins": {}})


@app.route('/api/getAllNewsItems', methods=['GET'])
def getNews():
    result =  eventApi.getAllNewsItems()
    if len(result) > 0:
        return jsonify({"responseCode": 200, "news": result})
    return jsonify({"responseCode": 400, "news": {} })

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
