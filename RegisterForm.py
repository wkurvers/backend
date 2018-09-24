from flask import jsonify
from passlib.handlers.pbkdf2 import pbkdf2_sha256

import checks
from Database import Persister, Person

def registerSubmit(form):

    firstName = form.get('firstName', None)
    lastName = form.get('lastName', None)
    email = form.get('email', None)
    password = form.get('password', None)

    firstName = firstName.strip()
    lastName = lastName.strip()
    firstName = firstName.replace(" ", "")
    lastName = lastName.replace(" ", "")
    email = email.replace(" ", "")
    firstName = firstName.lower()
    lastName = lastName.lower()
    email = email.lower()
    password = password.lower()

    if checks.checkSpecialChars([firstName,lastName]):
        return jsonify({
            "message": "Gebruik alstublieft geen speciale karakters in uw naam!"
        }), 400, {'ContentType': 'application/json'}

    if checks.checkSpecialCharsEmail(email):
        return jsonify({
            "message": "Please use no special characters in your email!"
        }), 400, {'ContentType': 'application/json'}

    if checks.emptyCheck([firstName, lastName, email, password]):
        return jsonify({
            "message": "Vul alstublieft alle velden in."
        }), 400, {'ContentType': 'application/json'}

    if checks.lengthSixtyFourCheck([firstName, lastName, email]):
        return jsonify({
            "message": "Vul alsublieft niet meer dan 64 karakters in."
        }), 400, {'ContentType': 'application/json'}

    password = form.get('password', None)
    check = checks.passwordLengthCheck(password)
    if check == [False, "short"]:
        return jsonify({
            "message": "Uw wachtwoord moet langer dan 5 karakters zijn."
        }), 400, {'ContentType': 'application/json'}
    if check == [False, "long"]:
        return jsonify({
            "message": "Uw wachtwoord moet korter zijn dan 64 karakters."
        }), 400, {'ContentType': 'application/json'}

    if Persister.checkEmailExistance(email):
        return jsonify({
            "message": "Dit emailadres bestaat al."
        }), 400, {'ContentType': 'application/json'}

    person = Person(
        firstname=firstName,
        lastname=lastName,
        email=email,
        password=pbkdf2_sha256.hash(password),
        points= 0,
        clearance= 0,
        license = True
    )

    return Persister.persist_object(person)
