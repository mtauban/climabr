from app import db
from enum import Enum


class pDay(Enum):
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    SUN = 7

class pLast(Enum):
    D = 24
    W = 168
    M = 5040
    Y = 61000


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


class Measurement(db.Model):
    id = id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.String(120), db.ForeignKey('sensor.id'))
    sensor = db.relationship('Sensor',
                             backref=db.backref('measurements', lazy='dynamic'))
    value = db.Column(db.String)
    date = db.Column(db.DateTime)

    def __init__(self, sensor, value, date=None):
        self.sensor = sensor
        if date is None:
            date = datetime.utcnow()
        self.date = date
        self.value = value

    def __repr__(self):
        return '<Measurement %r>' % self.id

    def toJSON(self):
        return {'sensor': self.sensor.toJSON(), 'date': self.date, 'value': self.value}


class Sensor(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(50))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                               backref=db.backref('sensors', lazy='dynamic'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location',
                               backref=db.backref('sensors', lazy='dynamic'))

    def __init__(self, id, name, category, location):
        self.id = id
        self.name = name
        self.category = category
        self.location = location

    def __repr__(self):
        return '<Sensor %r>' % self.id

    def toJSON(self):
        return {'id': self.id}


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    unit = db.Column(db.String(10))

    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

    def __repr__(self):
        return '<Category %r>' % self.name


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    position = db.Column(db.String(10))

    def __init__(self, name, position):
        self.name = name
        self.position = position

    def __repr__(self):
        return '<Location %r>' % self.name


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Enum(pDay))
    time = db.Column(db.TIME)
    ambiance_id = db.Column(db.Integer, db.ForeignKey('ambiance.id'))
    ambiance = db.relationship('Ambiance')

    def __init__(self, day, time, ambiance):
        self.day = day
        self.time = time
        self.ambiance = ambiance

    def __repr__(self):
        return '<Schedule %r>' % self.time


class Ambiance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    value = db.Column(db.Float)

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return '<Ambiance %r>' % self.name


class Config(db.Model):
    id = db.Column(db.String, primary_key=True)
    value = db.Column(db.String)

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def toJSON(self):
        return {self.id: self.value}

    def __repr__(self):
        return {self.id: self.value}
