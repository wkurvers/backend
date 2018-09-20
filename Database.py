import sqlalchemy as sqla
from flask import jsonify
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_login import UserMixin


conn = sqla.create_engine('mysql+pymysql://root:@127.0.0.1/bslim?host=127.0.0.1?port=3306')

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
    img = sqla.Column('img',sqla.VARCHAR(200))

class Content(Base):
    __tablename__ = 'content'
    id = sqla.Column('id', sqla.Integer, primary_key=True, autoincrement=True , unique=True)
    url = sqla.Column('url',sqla.VARCHAR(200))
    title = sqla.Column('title',sqla.VARCHAR(64))
    desc = sqla.Column('desc',sqla.VARCHAR(300))

class Particepant(Base):
    __tablename__ = 'particepant'
    person_id = sqla.Column('person_id',sqla.Integer,sqla.ForeignKey('person.id'), primary_key=True)
    event_id = sqla.Column('event_id',sqla.Integer,sqla.ForeignKey('event.id'), primary_key=True)
    event_scanned = sqla.Column('event_scanned',sqla.Boolean)


class Persister():

    def getPerson(self, id):
        db = Session()
        try:
            user = db.query(Person).filter(Person.id == id).first()
            db.close()
            return user
        except:
            db.rollback()
            db.close()

    def getEmail(self,email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()
        return user

    def getPassword(self, email):
        db = Session()
        user = db.query(Person.password).filter(Person.email == email).first()
        db.close()
        return user

    def getUserWithEmail(self,email):
        db = Session()
        user = db.query(Person).filter(Person.email == email).first()
        db.close()
        return user

    def persist_object(self, obj):
        db = Session()
        try:
            db.add(obj)
            db.commit()
        except:
            db.close()
            return False
        db.close()
        return True

    # Check if QR code is already scanned
    def isScanned(self,eventId,personId):
        db = Session()
        particepant = db.query(Particepant)\
            .filter(Particepant.event_id == eventId) \
            .filter(Particepant.person_id == personId)\
            .first()

        if particepant.event_scanned == None:
            return True
        else:
            return False
        db.close()

    def updateParticepantInfo(self,event_id, person_id):
        db = Session()
        particepant = db.query(Particepant) \
            .filter(Particepant.event_id == event_id ) \
            .filter(Particepant.person_id == person_id)\
            .first()

        particepant.event_scanned = True

        db.commit()
        db.close()
        return 200

    def checkEmailExistance(self, email):
        db = Session()
        if db.query(Person).filter(Person.email == email).count():
            db.close()
            return True
        db.close()
        return False

    def savePassword(self,password, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        person.password = pbkdf2_sha256.hash(password)

        db.commit()
        db.close()
        return 200

    def changePassword(self,email):
        pass

    def checkPoints(self,email):
        db = Session()
        points = db.query(Person.points).filter(Person.email == email).first()
        return points

    def addPoints(self, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        person.points = person.points + 1
        db.commit()
        db.close()
        return 200

    def substractPoint(self, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        if person.points <= 0:
            db.commit()
            db.close()
            return 400
        else:
            person.points = person.points - 1
            db.commit()
            db.close()
            return 200

    def resetStampCard(self, email):
        db = Session()
        person = db.query(Person).filter(Person.email == email).first()

        if person.points >= 15:
            person.points = 0

            db.commit()
            db.close()
            return 200




Base.metadata.create_all(conn)