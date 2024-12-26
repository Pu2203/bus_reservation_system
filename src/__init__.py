from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Change this to a random secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_reservation.db'  # Change to your database
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False