from Database import Persister, Particepant, Event
import string, random
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from flask import jsonify
import datetime

months = {'Jan': 'Jan', 
		  'Feb': 'Feb', 
		  'Mar': 'Mrt', 
		  'Apr': 'Apr', 
		  'May': 'Mei', 
		  'Jun': 'Jun', 
		  'Jul': 'Jul', 
		  'Aug': 'Aug', 
		  'Sep': 'Sep', 
		  'Oct': 'Okt', 
		  'Nov': 'Nov', 
		  'Dec': 'Dec'};

# returns 200 to indicate successful updating of the particepant info
def eventScanned(event_id, person_id):
    return Persister.updateParticepantInfo(event_id, person_id)

# Checks whether an event has already been scannend by the user scanning it.
def isScanned(eventId, person_id):
    return Persister.isScanned(eventId, person_id)

# returns 
def findEvent(qrCode):
	return Persister.findEvent(qrCode)

def deleteEvent(id):
	return Persister.remove_event(id)

def createEvent(id,name,begin,end,location,description,leader,img):
	print("HOI") 
	size=6
	chars=string.ascii_uppercase + string.digits
	unHashed = ''.join(random.choice(chars) for _ in range(size))
	qr_code = pbkdf2_sha256.hash(unHashed)
	if(id == '' or
       name == '' or
	   begin == '' or
	   end == '' or
	   location == '' or
	   description == '' or
	   leader== '' or
	   img==''):
		print(400)
		return 400
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
			qr_code=qr_code,
			created= datetime.datetime.now(),
			link= None
		)
	print(event)
	return Persister.persist_object(event)

def updateEvent(id,name,begin,end,location,description,leader,img):
	print("HOI") 
	size=6
	chars=string.ascii_uppercase + string.digits
	unHashed = ''.join(random.choice(chars) for _ in range(size))
	qr_code = pbkdf2_sha256.hash(unHashed)
	if(id == '' or
       name == '' or
	   begin == '' or
	   end == '' or
	   location == '' or
	   description == '' or
	   leader== '' or
	   img==''):
		return 400
	print("id " + str(id))
	print("name " + name)
	print("begin " + begin)
	print("end " + end)
	print("description " + description)
	print("leader " + str(leader))
	print("img " + img)
	print(id)
	return Persister.update_object(id,name,begin,end,location,description,leader,img, qr_code)

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
			return ({"responseCode": 500, "msg": "Could not add entry due to db error."})
	return ({"responseCode": 400, "msg": "Could not add participant entry because either some of the given data did not match or the entry already exists."})

def findSub(eventId, personId):
	return ({"found": Persister.checkParticepant(eventId, personId)})

def unSubToEvent(eventId, personId):
	if Persister.checkParticepant(eventId, personId):
		print("particepant exists")
		particepant = Persister.getParticepant(eventId, personId)
		print(particepant)
		if Persister.remove_object(particepant) == 200:
			return ({"responseCode": 200, "msg": "Removed particepant entry."})
		else:
			return ({"responseCode": 500, "msg": "Could not remove entry due to db error."})
	return ({"responseCode": 400, "msg": "Could not remove participant entry because either some of the given data did not match or the entry does not exists."})

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
		beginTime = begin.strftime('%H:%M')

		end = event['end']
		endDay = end.strftime('%d')
		endMonth = end.strftime('%b')
		endTime = end.strftime('%H:%M')
		result.append({"id": event['id'], "name": event['name'], "begin": beginDay, "beginMonth": months[beginMonth], "end": endDay, "endMonth": months[endMonth], "endTime": endTime,
    	               "location": event['location'], "desc": event['desc'], "leader": leader, "cancel": event['cancel'], "img": event['img'],"qrCode": event['qr_code'],
    	               "created": created,"link":event['link'],"photo":photo, "subscribed": None });

	return result


def searchNews(searchString):
	found = Persister.searchNews(searchString)
	result = []
	for newsName in found:
		news = found[newsName]

		result.append({"id": news['id'], "url": news['url'], 'title': news['title'], 'desc': news['desc'], 'created': news['created']});
	return result


def getAllEvents():
	events = Persister.getAllEvents()
	result = []
	if events != 400:
		for event in events:
			leader = Persister.getLeader(event.leader)
			photo = Persister.getProfilePhoto(event.leader)
			createDate = event.created
			created = createDate.strftime('%m/%d/%Y')
			
			begin = event.begin
			beginDay = begin.strftime('%d')
			beginMonth = begin.strftime('%b')
			beginTime = begin.strftime('%H:%M')

			end = event.end
			endDay = end.strftime('%d')
			endMonth = end.strftime('%b')
			endTime = end.strftime('%H:%M')
			
			result.append({"id": event.id, "name": event.name, "begin": beginDay,"beginMonth": months[beginMonth], "beginTime": beginTime, "end": endDay, "endMonth": months[endMonth], "endTime": endTime,
							"location": event.location, "desc": event.desc, "leader": leader, "cancel": event.cancel, "img": event.img,"qrCode": event.qr_code,
							"created": created,"link":event.link,"photo":photo, "subscribed": None  })
	
	return result


def getAllNewsItems():
	news = Persister.getAllNewsItems()

	result = []
	if news != 400:
		for item in news:
			result.append({"id": item.id, "url": item.url, "title": item.title,"desc": item.desc,"created": item.created,"link":item.link})

	return result

def getAllSubs(id):
    eventIds = Persister.getAllSubs(id)
    print(eventIds)

    result = []
    if eventIds != 400:
        for item in eventIds:
            print(item[0])
            eventName = Persister.getEventName(item[0])
            result.append(
                {"title": eventName})

    return result
