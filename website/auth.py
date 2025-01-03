from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from databases.user_dao import UserDAO
from .models import User
import re

auth_bp = Blueprint('auth', __name__)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return UserDAO.get_user_by_id(user_id)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Password validation
        if not password:
            flash('Password field cannot be blank')
            return redirect(url_for('auth.register'))
        if not confirm_password:
            flash('Confirm password field cannot be blank')
            return redirect(url_for('auth.register'))
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.register'))
        if len(password) < 6 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            flash('Password is too weak')
            return redirect(url_for('auth.register'))
        
        # Check if the username already exists
        existing_user = UserDAO.get_user_by_username(username)
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('auth.register'))

        # Create a new user
        UserDAO.add_user(username, password, name, phone_number)
        flash('Registration successful! You can now log in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = UserDAO.get_user_by_username(username)
        if user and UserDAO.check_password(user.password_hash, password):
            login_user(user)
            flash('Login successful!')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('view.home'))  # Redirect to a home page or dashboard
        else:
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('view.index'))