from routes import db
from flask_login.mixins import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    address = db.Column(db.String(500), nullable = False)
    credits = db.Column(db.Integer)
    password = db.Column(db.String)
    def __repr__(self):
        return f"Username: {self.name}"
    def check_password(self,password):
        return self.password == password