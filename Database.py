import sqlalchemy as sqla
from flask import jsonify
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_login import UserMixin
import checks
import re


conn = sqla.create_engine('mysql+pymysql://root:@localhost/bslim?charset=utf8')

Session = scoped_session(sessionmaker(bind=conn))

Base = declarative_base()

class Person(Base,UserMixin):
    __tablename__ = 'person'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True, unique=True)
    firstname = sqla.Column('firstname', sqla.VARCHAR(64))
    lastname = sqla.Column('lastname', sqla.VARCHAR(64))
    email = sqla.Column('email', sqla.VARCHAR(64), unique=True)
    password = sqla.Column('password', sqla.VARCHAR(64))
    points = sqla.Column('points',sqla.Integer)
    clearance = sqla.Column('clearance',sqla.Integer)
    license = sqla.Column('license',sqla.Boolean)
    authenticated = sqla.Column('authenticated', sqla.Boolean)
    biography = sqla.Column('biography', sqla.VARCHAR(1000))
    profilePhoto = sqla.Column('profilePhoto', sqla.VARCHAR(100000))

class Event(Base):
    __tablename__ = 'event'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True , unique=True)
    name = sqla.Column('name',sqla.VARCHAR(64))
    begin = sqla.Column('begin',sqla.DATETIME)
    end = sqla.Column('end',sqla.DATETIME)
    location = sqla.Column('location',sqla.VARCHAR(64))
    desc = sqla.Column('desc',sqla.VARCHAR(200))
    leader = sqla.Column('leader',sqla.Integer,sqla.ForeignKey('person.id'))
    cancel = sqla.Column('cancel',sqla.Integer)
    img = sqla.Column('img',sqla.VARCHAR(100000))
    qr_code = sqla.Column('qr_code',sqla.VARCHAR(200))
    created = sqla.Column('created',sqla.DATETIME)
    link = sqla.Column('link',sqla.VARCHAR(400))

class Content(Base):
    __tablename__ = 'content'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True , unique=True)
    url = sqla.Column('url',sqla.VARCHAR(400))
    title = sqla.Column('title',sqla.VARCHAR(64))
    desc = sqla.Column('desc',sqla.VARCHAR(300))

class Particepant(Base):
    __tablename__ = 'particepant'
    person_id = sqla.Column('person_id',sqla.Integer,sqla.ForeignKey('person.id'), primary_key=True)
    event_id = sqla.Column('event_id',sqla.Integer,sqla.ForeignKey('event.id'), primary_key=True)
    event_scanned = sqla.Column('event_scanned',sqla.Boolean)

class Media(Base):
    __tablename__ = 'media'
    event_id = sqla.Column('event_id',sqla.Integer,sqla.ForeignKey('event.id'), primary_key=True)
    url = sqla.Column('url',sqla.VARCHAR(400))




class Persister():
    def getPerson(id):
        db = Session()
        try:
            user = db.query(Person).filter(Person.id == id).first()
            db.close()
            return user
        except:
            db.rollback()
            db.close()

    def getEmail(email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()

        if user is not None:
            return user.email
        else:
            return None

    def loginUser(user):
        db = Session()
        person = db.query(Person).filter(Person.id == user.id).first()
        person.authenticated = True
        db.commit()
        db.close()
        return True

    def logoutUser(user):
        db = Session()
        person = db.query(Person).filter(Person.id == user.id).first()
        person.authenticated = False
        db.commit()
        db.close()
        return True
        return False

    def getPassword(email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()
        if user is not None:
            return user.password
        else:
            return None

    def getUserWithEmail(email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()
        return user

    def persist_object(obj):
        db = Session()
        try:
            db.add(obj)
            db.commit()
        except:
            db.close()
            return 400
        db.close()
        return 200

    # Check if QR code is already scanned
    # If the user has not subscribed himself to the event and both the user and the event exists the user is automaticly subscribed to the event.
    def isScanned(eventId,personId):
        db = Session()
        particepant = db.query(Particepant).filter(Particepant.person_id == personId)\
                                           .filter(Particepant.event_id == eventId)\
                                           .first()
        db.close()
        if particepant == None:
            if(db.query(Event).filter(Event.id == eventId).count()):
                if(db.query(Person).filter(Person.id == personId).count()):
                    db = Session()
                    newParticepant = Particepant(
                        person_id=personId,
                        event_id=eventId,
                        event_scanned=0
                    )
                    db.add(newParticepant)
                    db.commit()
                    db.close()
                    particepant = db.query(Particepant).filter(Particepant.person_id == personId)\
                                           .filter(Particepant.event_id == eventId)\
                                           .first()
                    return particepant.event_scanned
        elif particepant.event_scanned:
            return 400
        return 200

    # Checks whether or not a particepant entry or beloging events and persons already exists
    def checkParticepant(eventId, personId):
        db = Session()
        if(db.query(Event).filter(Event.id == eventId).count()):
                if(db.query(Person).filter(Person.id == personId).count()):
                    if(db.query(Particepant).filter(Particepant.person_id == personId).filter(Particepant.event_id == eventId).count()):
                        db.close()
                        return True
        db.close()
        return False

    # Marks the particepant entry as scannend and adds a point to the user account
    def updateParticepantInfo(event_id, person_id):
        db = Session()
        particepant = db.query(Particepant).filter(Particepant.person_id == person_id)\
                                           .filter(Particepant.event_id == event_id)\
                                           .first()

        person = db.query(Person).filter(Person.id == person_id).first()
        person.points = person.points + 1

        particepant.event_scanned = True
        db.commit()
        db.close()
        return "200"

    def checkEmailExistance(email):
        db = Session()
        if db.query(Person).filter(Person.email == email).count():
            db.close()
            return True
        db.close()
        return False

    # searches for an event with a specifyc qr_code value
    # returns False if one isn't found otherwise returns the event
    def findEvent(qrCode):
        db = Session()
        if db.query(Event).filter(Event.qr_code == qrCode).count():
            event = db.query(Event).filter(Event.qr_code == qrCode).first()
            db.close()
            return event
        db.close()
        return False

    def searchEvent(searchString):
        db=Session()
        #define month numbers to translate user searchString if it contains months
        months = {
            "january" : '1',
            "february" : '2',
            "maart" : '3',
            "april" : '4',
            "mei" : '5',
            "juni" : '6',
            "juli" : '7',
            "augustus" : '8',
            "september" : '9',
            "oktober" : '10',
            "november" : '11',
            "december" : '12'
        }

        #declare all dicts: to be filled by query results later
        returnData = {}
        leaders = {}
        eventsByLeader = {}
        eventsByBegin = {}
        eventsByEnd = {}

        #query the db on event names containging the search string
        eventsName = db.query(Event).filter(Event.name.contains(searchString)).all()

        #query the db for persons whose first and/or last name contain the search string
        personsFirstName = db.query(Person).filter(Person.firstname.contains(searchString)).all()
        personsLastName = db.query(Person).filter(Person.lastname.contains(searchString)).all()

        #Convert the user query to a date query
        for month in months:
            if month in searchString.lower():
                #searchString is a date query
                monthNumber = months[month]
                if any(char.isdigit() for char in searchString):
                    numbers = re.findall(r'\d+', searchString)
                    dayNumber = numbers[0]
                    if int(dayNumber) < 10:
                        dayNumber = "0" + dayNumber
                    yearNumber = ''
                    if len(numbers) > 1:
                        yearNumber = numbers[1] + '-'
                    dateString = yearNumber + monthNumber + "-" + dayNumber
                    eventsByBegin = db.query(Event).filter(Event.begin.contains(dateString)).all()
                    eventsByEnd = db.query(Event).filter(Event.end.contains(dateString)).all()
                else:
                    eventsByBegin = db.query(Event).filter(Event.begin.contains(monthNumber)).all()
                    eventsByEnd = db.query(Event).filter(Event.end.contains(monthNumber)).all()
            
        for event in eventsByBegin:
            if event.name not in returnData:
                eventEntry = {}
                person = db.query(Person).filter(Person.id == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.id
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link

                returnData[event.name] = eventEntry

        for event in eventsByEnd:
            if event.name not in returnData:
                eventEntry = {}
                person = db.query(Person).filter(Person.id == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.id
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link

                returnData[event.name] = eventEntry

        #loop through query result and add the person to the leaders dict if it isn't there already
        for person in personsFirstName:
            if person.id not in leaders:
                leaders[person.id] = person

        #loop through query result and add the person to the leaders dict if it isn't there already
        for person in personsLastName:
            if person.id not in leaders:
                leaders[person.id] = person

        #loop through leaders dict and if it exists get all events that that person leads, if it isn't already in the returnData dict it adds the event
        for personId in leaders:
            person = leaders[personId]
            if db.query(Event).filter(Event.leader == person.id).count():
                events = db.query(Event).filter(Event.leader == person.id).all()
                for event in events:
                    if event.name not in returnData:
                        eventEntry = {}
                        eventEntry['id'] = event.id
                        eventEntry['name'] = event.name
                        eventEntry['begin'] = event.begin
                        eventEntry['end'] = event.end
                        eventEntry['location'] = event.location
                        eventEntry['desc'] = event.desc
                        eventEntry['leader'] = person.id
                        eventEntry['cancel'] = event.cancel
                        eventEntry['img'] = event.img
                        eventEntry['qr_code'] = event.qr_code
                        eventEntry['created'] = event.created
                        eventEntry['link'] = event.link
    
                        returnData[event.name] = eventEntry
        
        #loop through eventsName dict and if it isn't already in the returnData dict it adds the event
        for event in eventsName:
            eventEntry = {}
            if event.name not in returnData:
                person = db.query(Person).filter(Person.id == event.leader).first()
                eventEntry['id'] = event.id
                eventEntry['name'] = event.name
                eventEntry['begin'] = event.begin
                eventEntry['end'] = event.end
                eventEntry['location'] = event.location
                eventEntry['desc'] = event.desc
                eventEntry['leader'] = person.id
                eventEntry['cancel'] = event.cancel
                eventEntry['img'] = event.img
                eventEntry['qr_code'] = event.qr_code
                eventEntry['created'] = event.created
                eventEntry['link'] = event.link
    
                returnData[event.name] = eventEntry
        db.close()
        return returnData

    def savePassword(password, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        person.password = password

        db.commit()
        db.close()
        return 200

    def changePassword(id, oldPassword, newPassword):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()
        # hashedNewPassword = pbkdf2_sha256.hash(newPassword) CHANGE BACK
        hashedNewPassword = newPassword
        if person.password == oldPassword:
            if checks.emptyCheck([newPassword]) or len(newPassword) < 5 or person.password == hashedNewPassword:
                return 400
            else:
                person.password = hashedNewPassword
    
                db.commit()
                db.close()
                return 200
        return 400


    def checkPoints(id):
        db = Session()
        points = db.query(Person.points).filter(Person.id == id).first()
        return points

    def addPoints(id):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()

        person.points = person.points + 1
        db.commit()
        db.close()
        return 200

    def substractPoint(id):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()

        if person.points <= 0:
            db.commit()
            db.close()
            return 400
        else:
            person.points = person.points - 1
            db.commit()
            db.close()
            return 200

    def resetStampCard(id):
        db = Session()
        person = db.query(Person).filter(Person.id == id).first()

        if person.points >= 15:
            person.points = 0

            db.commit()
            db.close()
            return 200

    def saveMedia(url,eventName):
        db = Session()

        if db.query(Event).filter(Event.name == eventName).count():
            eventId = db.query(Event.id).filter(Event.name == eventName).first()

            newMedia = Media(
                event_id=eventId,
                url = url

            )

            db.add(newMedia)
            db.commit()
            db.close()
            return 200
        else:
            return 400

    def addProfilePhoto(url,id):
        db = Session()

        if db.query(Person).filter(Person.id == id).count():

            person = db.query(Person).filter(Person.id == id).first()
            person.profilePhoto = url

            db.commit()
            db.close()

            return 200
        else:
            return 400

    def getProfilePhoto(id):
        db = Session()

        if db.query(Person).filter(Person.id == id).count():

            profilePhoto = db.query(Person.profilePhoto).filter(Person.id == id).first()
            db.close()

            return profilePhoto
        else:
            return 400

    def getLeader(id):
        db = Session()

        if db.query(Person).filter(Person.id == id).count():
            fName = db.query(Person.firstname).filter(Person.id == id).first()
            lName = db.query(Person.lastname).filter(Person.id == id).first()

            name = (fName, " " ,lName)
            db.close()
            return name
        else:
            return "Onbekend"

    def getAllEvents():
        db = Session()
        if db.query(Event).count():
            events = db.query(Event).all()
            db.close()
            return events
        else:
            return 400





Base.metadata.create_all(conn)