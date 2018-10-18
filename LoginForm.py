import sys, UserApi
from flask_login import login_user, current_user
from passlib.hash import pbkdf2_sha256
from Database import Persister, Person
import requests
import json

def loginUser(form):
    emailLogin = form.get('email')
    passwordLogin = form.get('password')
    dbEmail = UserApi.getEmail(emailLogin)

    if dbEmail is None:
        return {"responseCode": 400, "boolean": "false", "userId": None, "clearance": None, "msg": "Email klopt niet"}

    dbPassword = UserApi.getPassword(emailLogin)

    if dbPassword == passwordLogin:
        user = UserApi.getUserByEmail(emailLogin)
        Persister.loginUser(user)
        return {"responseCode": 200, "boolean": "true", "userId": user.id, "clearance": user.clearance, "msg": "OK"}

    else:
        return {"responseCode": 400, "boolean": "false", "userId": None, "clearance": None, "msg": "Wachtwoord klopt niet"}

def logoutUser(form):
    user = Persister.getPerson(form.get('id'))
    if Persister.logoutUser(user):
        return {"responseCode": 200, "boolean": True}
    return {"responseCode": 500, "boolean": False}


def checkLogin(form):
    user = Persister.getPerson(form.get('id'))
    return user.authenticated
