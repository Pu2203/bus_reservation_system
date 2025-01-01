from flask import Flask
from flask_login import LoginManager
from databases.user_dao import UserDAO
from databases.bus_dao import BusDAO
from databases.reservation_dao import ReservationDAO


def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # Change this to a random secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_reservation.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return UserDAO.get_user_by_id(user_id)

    from .admin import admin
    from .auth import auth_bp
    from .view import view_bp
    
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(view_bp, url_prefix='/')

    return app