from Database import Persister, Particepant, Event
import string, random
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import jsonify
import datetime


# returns 200 to indicate successful updating of the particepant info
def eventScanned(event_id, person_id):
    return Persister.updateParticepantInfo(event_id, person_id)

# Checks whether an event has already been scannend by the user scanning it.
def isScanned(eventId, person_id):
    return Persister.isScanned(eventId, person_id)

# returns 
def findEvent(qrCode):
	return Persister.findEvent(qrCode)

def createEvent(name,begin,end,location,description,leader,img):
	size=6
	chars=string.ascii_uppercase + string.digits
	unHashed = ''.join(random.choice(chars) for _ in range(size))
	qr_code = pbkdf2_sha256.hash(unHashed)
	if(name == '' or
	   begin == '' or
	   end == '' or
	   location == '' or
	   description == '' or
	   leader== '' or
	   img==''):
		return 400
	event = Event(
			name=name,
			begin=begin,
			end=end,
			location=location,
			desc=description,
			leader=leader,
			cancel=0,
			img=img,
			qr_code=qr_code,
			created= datetime.datetime.now(),
			link= None
		)
	return Persister.persist_object(event)

def subToEvent(eventId, personId):
	if not Persister.checkParticepant(eventId, personId):
		particepant = Particepant(
				person_id=personId,
				event_id=eventId,
				event_scanned=0
			)
		if Persister.persist_object(particepant) == 200:
			return ({"responseCode": 200, "msg": "Added particepant entry."})
		else:
			return ({"responseCode": 400, "msg": "Could not add entry due to db error."})
	return ({"responseCode": 400, "msg": "Could not add participant entry because either some of the given data did not match or the entry already exists."})

def saveMedia(url, eventName):
    return Persister.saveMedia(url, eventName)

def searchEvent(searchString):
	found = Persister.searchEvent(searchString)
	result = []
	for eventName in found:
		event = found[eventName]
		leader = Persister.getLeader(event['leader'])
		photo = Persister.getProfilePhoto(event['leader'])
		createDate = event['created']
		created = createDate.strftime('%m/%d/%Y')
		begin = event['begin']
		beginDay = begin.strftime('%d')
		beginMonth = begin.strftime('%b')

		result.append({"id": event['id'], "name": event['name'], "begin": beginDay,"beginMonth": beginMonth,"end": event['end'],
    	               "location": event['location'], "desc": event['desc'], "leader": leader, "cancel": event['cancel'], "img": event['img'],"qrCode": event['qr_code'],
    	               "created": created,"link":event['link'],"photo":photo });

	return result

def getAllEvents():
    events = Persister.getAllEvents()
    if events != 400:
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

    return result