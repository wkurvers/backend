from flask_login import LoginManager, current_user, login_required, logout_user
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file, make_response, session
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

@app.route('/api/qrEvent', method=['GET'])
def eventScanned():
    eventId = request.args.get('eventId', None)
    personId = request.args.get('personId', None)
    if eventApi.isScanned(eventId, personId):
        return jsonify(False)
    else:
        return eventApi.eventScanned(eventId,personId)

@app.route('/register', methods=['POST'])
def registerHandler():
    return RegisterForm.registerSubmit(request.args)

@app.route('/api/passRecovery', methods=['GET'])
def getNewPassword(size=6, chars=string.ascii_uppercase + string.digits):
    email = request.args.get('email',None)
    temp =  ''.join(random.choice(chars) for _ in range(size))
    UserApi.saveNewPassword(temp,email)
    return temp