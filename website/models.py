from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password_hash, email=None, phone_number=None, gender=None, balance=0.0, name=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.phone_number = phone_number
        self.gender = gender
        self.balance = balance
        self.name = name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __str__(self):
        return f'<User {self.username}>'
    
class Bus:
    def __init__(self, id, bus_number, route, total_seats, available_seats, time, price):
        self.id = id
        self.bus_number = bus_number
        self.route = route
        self.total_seats = total_seats
        self.available_seats = available_seats
        self.time = time
        self.price = price