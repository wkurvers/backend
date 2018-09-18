from Database import Persister

def getPerson(person_id):
    return Persister.getPerson(person_id)

def getUserByEmail(emailLogin):
    return Persister.getUserWithEmail(emailLogin)

def getEmail(emailLogin):
    Persister.getEmail(emailLogin)

def getPassword(password):
    Persister.getPassword(password)

