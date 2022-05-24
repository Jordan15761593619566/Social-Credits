from routes import db
from flask_login.mixins import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80), nullable = False)
    address = db.Column(db.String(500))
    credits = db.Column(db.Integer)
    password = db.Column(db.String)
    permissions = db.Column(db.String(20))
    def __repr__(self):
        return f"Username: {self.name}"
    def check_password(self,password):
        return self.password == password
    activities_done = db.relationship('User_Activities', back_populates='user', cascade='all, delete-orphan')

class Activities(db.Model):
    __tablename__ = 'Activities'

    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.Integer)
    value = db.Column(db.Integer)
    user_activities = db.relationship('User_Activities', back_populates='activity', cascade='all, delete-orphan')

class User_Activities(db.Model):
    __tablename__ = 'User_Activities'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable = False)
    activity_id = db.Column(db.Integer, db.ForeignKey('Activities.id'), nullable = False)

    user = db.relationship('User')
    activity = db.relationship('Activities')