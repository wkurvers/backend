import sys, UserApi
from flask_login import login_user
from passlib.hash import pbkdf2_sha256

def loginUser(form):
    emailLogin = form.get('email')
    password_candidate = form.get('password')
    dbEmail = UserApi.getEmail(emailLogin)[0]
    dbPassword = UserApi.getPassword(emailLogin)[0]
    print
    if dbPassword == None or dbEmail == None:
        return False
    elif dbPassword == password_candidate:
        user = UserApi.getUserByEmail(emailLogin)
        login_user(user)
        return user