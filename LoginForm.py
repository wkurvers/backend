import sys, UserApi
from flask_login import login_user, current_user
from passlib.hash import pbkdf2_sha256
from Database import Persister, Person

def loginUser(form):
    emailLogin = form.get('email')
    password_candidate = form.get('password')
    dbEmail = UserApi.getEmail(emailLogin)[0]
    dbPassword = UserApi.getPassword(emailLogin)[0]
    if dbPassword == None or dbEmail == None:
        return False
    elif dbPassword == password_candidate:
        user = UserApi.getUserByEmail(emailLogin)
        Persister.loginUser(user)
        return user
    else:
        return False

def logoutUser(form):
    user = Persister.getPerson(form.get('id'))
    return Persister.logoutUser(user)

def checkLogin(form):
    user = Persister.getPerson(form.get('id'))
    return user.authenticated

