import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User

class UserDAO:
    @staticmethod
    def add_user(username, password, name, phone_number, email=None, gender=None):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, name, email, phone_number, gender)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, name, email, phone_number, gender))
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_by_username(username):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        
        conn.close()
        
        if user_data:
            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                phone_number=user_data[4],
                gender=user_data[5],
                balance=user_data[6],
                name=user_data[7]
            )
        return None

    @staticmethod
    def get_user_by_id(user_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        conn.close()
        
        if user_data:
            return User(
                id=user_data[0],
                username=user_data[1],
                password_hash=user_data[2],
                email=user_data[3],
                phone_number=user_data[4],
                gender=user_data[5],
                balance=user_data[6],
                name=user_data[7]
            )
        return None

    @staticmethod
    def check_password(stored_password_hash, password):
        return check_password_hash(stored_password_hash, password)

    @staticmethod
    def update_user(user_id, username, email, phone_number, gender, name):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users
            SET username = ?, email = ?, phone_number = ?, gender = ?, name = ?
            WHERE id = ?
        ''', (username, email, phone_number, gender, name, user_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def update_balance(user_id, amount):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users
            SET balance = balance + ?
            WHERE id = ?
        ''', (amount, user_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_users():
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, name, phone_number, balance FROM users')
        users_data = cursor.fetchall()
        
        conn.close()
        
        users = []
        for user_data in users_data:
            users.append(User(
                id=user_data[0],
                username=user_data[1],
                password_hash=None,  # Password hash is not selected in the query
                email=None,  # Email is not selected in the query
                phone_number=user_data[3],
                gender=None,  # Gender is not selected in the query
                balance=user_data[4],
                name=user_data[2]  # Name is not selected in the query
            ))
        return users

    @staticmethod
    def update_password(user_id, new_password):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        password_hash = generate_password_hash(new_password)
        
        cursor.execute('''
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        conn.close()