from Database import Persister

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
        return Persister.savePasswordHashed(temp,email)
    else:
        return 400

def changePassword(email, newPassword):
    return Persister.changePassword(email, newPassword)

def checkPoints(id):
    return Persister.checkPoints(id)

def addPoints(id):
    return Persister.addPoints(id)


def substractPoint(id):
    return Persister.substractPoint(id)


def resetStampCard(id):
    return Persister.resetStampCard(id)


