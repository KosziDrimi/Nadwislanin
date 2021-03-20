from project.app import db
from flask_login import UserMixin



class User(db.Model, UserMixin):
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    is_admin = db.Column(db.Boolean)
    
    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = password
        self.is_admin = is_admin


class Reservation(db.Model):

    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    duration = db.Column(db.String)
    numbers = db.Column(db.String)
    feedback = db.Column(db.Text)
    new = db.Column(db.Boolean)
    confirmation = db.Column(db.Text)
    email_text = db.Column(db.Text)
    
    def __init__(self, name, email, date, time, duration, numbers, feedback, new=True, confirmation=None, email_text=None):
      
        self.name = name
        self.email = email
        self.date = date
        self.time = time
        self.duration = duration
        self.numbers = numbers
        self.feedback = feedback
        self.new = new
        self.confirmation = confirmation 
        self.email_text = email_text
        
    def __repr__(self):
        return f"""Reservation details: {self.id}
             {self.name} {self.email}
             {self.date} {self.time}
             {self.duration} {self.numbers}
             {self.feedback} {self.new}"""
             
