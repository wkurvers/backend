from Database import Persister, Particepant, Event
import string, random
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import jsonify


# returns 200 to indicate successful updating of the particepant info
def eventScanned(event_id, person_id):
    return Persister.updateParticepantInfo(event_id, person_id)

# Checks whether an event has already been scannend by the user scanning it.
def isScanned(eventId, person_id):
    return Persister.isScanned(eventId, person_id)

# returns 
def findEvent(qrCode):
	return Persister.findEvent(qrCode)

def createEvent(id,name,begin,end,location,description,leader,img):
	size=6
	chars=string.ascii_uppercase + string.digits
	unHashed = ''.join(random.choice(chars) for _ in range(size))
	qr_code = pbkdf2_sha256.hash(unHashed)

	event = Event(
			id=id,
			name=name,
			begin=begin,
			end=end,
			location=location,
			desc=description,
			leader=leader,
			cancel=0,
			img=img,
			qr_code=qr_code
		)
	return Persister.persist_object(event)


def saveMedia(url, eventName):
    return Persister.saveMedia(url, eventName)

def getAllEvents():
	events = Persister.getAllEvents()
	result = []
	for event in events:
         leader = Persister.getLeader(event.leader)
         photo = Persister.getProfilePhoto(event.leader)
         createDate = event.created
         created = createDate.strftime('%m/%d/%Y')
         begin = event.begin
         beginDay = begin.strftime('%d')
         beginMonth = begin.strftime('%b')




         result.append({"id": event.id, "name": event.name, "begin": beginDay,"beginMonth": beginMonth,"end": event.end,
                       "location": event.location, "desc": event.desc, "leader": leader, "cancel": event.cancel, "img": event.img,"qrCode": event.qr_code,
                       "created": created,"link":event.link,"photo":photo })
    
	return jsonify(result)

