from Database import Persister,Particepant


def eventScanned(event_id, person_id):
    return Persister.updateParticepantInfo(event_id, person_id)


def isScanned(eventId):
    return Persister.isScanned(eventId)