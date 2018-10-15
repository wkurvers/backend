from Database import Persister
import datetime

def getPerson(person_id):
    return Persister.getPerson(person_id)

def getUserByEmail(emailLogin):
    return Persister.getUserWithEmail(emailLogin)

def getEmail(emailLogin):
    return Persister.getEmail(emailLogin)

def getPassword(email):
    return Persister.getPassword(email)


def saveNewPassword(temp,email):
    if Persister.checkEmailExistance(email):
        return Persister.savePassword(temp,email) #change to hashed
    else:
        return 400

def changePassword(id, oldPassword, newPassword):
    return Persister.changePassword(id, oldPassword, newPassword)

def changeEmail(id):
    return Persister.changeEmail(id)

def checkSecCode(oldEmail, secCode):
    return Persister.checkSecCode(oldEmail, secCode)

def changeUserEmail(oldEmail, newEmail):
    return Persister.changeUserEmail(oldEmail, newEmail)

def checkPoints(id):
    return Persister.checkPoints(id)

def addPoints(id):
    return Persister.addPoints(id)


def substractPoint(id):
    return Persister.substractPoint(id)


def resetStampCard(id):
    return Persister.resetStampCard(id)

def addProfilePhoto(url):
    return Persister.addProfilePhoto(url,id)

def getProfilePhoto(id):
    return Persister.getProfilePhoto(id)

def getAllAdmins():
    admins = Persister.getAllAdmins()
    if admins != 400:
        result = []
        for admin in admins:
            result.append({"id": admin.id, "firstName": admin.firstname, "lastName": admin.lastname})

    return result


def createNewsItem(title, content, img):
    if (title == '' or
            content == '' or
            img == ''):
        return 400
    item = Content(
        url=img,
        title=title,
        desc=content,
        link=None,
        created=datetime.datetime.now()
    )
    return Persister.persist_object(item)