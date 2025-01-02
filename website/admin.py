from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from databases.user_dao import UserDAO
from databases.bus_dao import BusDAO
from flask_login import login_required

admin = Blueprint('admin', __name__)

@admin.before_request
def check_admin():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to access this page.')
        return redirect(url_for('auth.login'))
    user = UserDAO.get_user_by_id(user_id)
    if user is None or user.username != 'admin':
        flash('You do not have permission to access this page.')
        return redirect(url_for('view.home'))

# Route for adding a bus
@admin.route('/add_bus', methods=['GET', 'POST'])
@login_required
def add_bus_route():
    if request.method == 'POST':
        bus_number = request.form['bus_number']
        route = request.form['route']
        total_seats = request.form['total_seats']
        time = request.form['time']
        price = request.form['price']
        BusDAO.add_bus(bus_number, route, total_seats, time, price)
        flash('Bus added successfully!')
        return redirect(url_for('view.view_buses_route'))
    return render_template('add_bus.html')

# Route for editing a bus
@admin.route('/edit_bus/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def edit_bus(bus_id):
    bus = BusDAO.get_bus(bus_id)
    if bus is None:
        flash('Bus not found.')
        return redirect(url_for('view.view_buses_route'))
    
    if request.method == 'POST':
        bus_number = request.form['bus_number']
        route = request.form['route']
        total_seats = int(request.form['total_seats'])
        available_seats = int(request.form['available_seats'])
        time = request.form['time']
        price = request.form['price']
        
        BusDAO.update_bus(bus_id, bus_number, route, total_seats, available_seats, time, price)
        flash('Bus details updated successfully!')
        return redirect(url_for('view.view_buses_route'))
    
    return render_template('edit_bus.html', bus=bus)

# Route for deleting a bus
@admin.route('/delete_bus/<int:bus_id>', methods=['POST'])
@login_required
def delete_bus(bus_id):
    BusDAO.delete_bus_from_db(bus_id)
    flash('Bus deleted successfully!')
    return redirect(url_for('view.view_buses_route'))

# Route for managing accounts
@admin.route('/manage_accounts', methods=['GET', 'POST'])
@login_required
def manage_accounts():
    if request.method == 'POST':
        action = request.form['action']
        target_user_id = int(request.form['user_id'])
        if action == 'update_balance':
            amount = float(request.form['amount'])
            UserDAO.update_balance(target_user_id, amount)
        elif action == 'update_password':
            new_password = request.form['new_password']
            UserDAO.update_password(target_user_id, new_password)
        flash('Account updated successfully!')
        return redirect(url_for('admin.manage_accounts'))
    users = UserDAO.get_all_users()
    return render_template('manage_accounts.html', users=users)