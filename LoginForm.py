import sys, UserApi
from flask_login import login_user
from passlib.hash import pbkdf2_sha256

def loginUser(form):
    emailLogin = form.get('email')
    password_candidate = form.get('password')
    dbEmail = UserApi.getEmail(emailLogin)
    dbPassword = UserApi.getPassword(emailLogin)
    if dbPassword == None or dbEmail == None:
        print('login failed', file=sys.stderr)
        return 401
    if dbPassword == password_candidate:
        print('logged in', file=sys.stderr)
        user = UserApi.getUserByEmail(emailLogin)
        login_user(user)
        return 200
    else: return 401