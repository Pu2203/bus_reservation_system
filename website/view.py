from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from databases.user_dao import UserDAO
from databases.bus_dao import BusDAO
from databases.reservation_dao import ReservationDAO
from io import BytesIO
from flask import send_file
import qrcode
from .trie import Trie

view_bp = Blueprint('view', __name__)

trie = Trie()

@view_bp.before_app_request
def load_routes_into_trie():
    buses = BusDAO.view_buses()
    for bus in buses:
        trie.insert(bus.route)

@view_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '')
    suggestions = trie.search(query)
    return jsonify(suggestions)

# Custom Jinja2 filter to check if the user is admin
@view_bp.app_template_filter('is_admin')
def is_admin(user_id):
    user = UserDAO.get_user_by_id(user_id)
    return user and user.username == 'admin'

# Route for the index page
@view_bp.route('/')
def index():
    user_id = session.get('user_id')
    user = None
    balance = None
    if user_id:
        user = UserDAO.get_user_by_id(user_id)
        balance = user.balance
    return render_template('index.html', user=user, balance=balance)

# Home route (after login)
@view_bp.route('/home')
@login_required
def home():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view the home page.')
        return redirect(url_for('auth.login'))
    
    user = UserDAO.get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    
    username = user.username
    balance = user.balance
    return render_template('home.html', username=username, balance=balance, user=user)

# Route for viewing buses
@view_bp.route('/view_buses', methods=['GET', 'POST'])
@login_required
def view_buses_route():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view buses.')
        return redirect(url_for('auth.login'))
    user = UserDAO.get_user_by_id(user_id)
    
    sort_by = request.args.get('sort_by')
    search_query = request.form.get('search_query')
    
    buses = BusDAO.view_buses(sort_by=sort_by, search_query=search_query)
    buses = [bus for bus in buses if bus.available_seats > 0]
    balance = user.balance
    return render_template('view_buses.html', buses=buses, user=user, balance=balance)

# Route for viewing reservations
@view_bp.route('/view_reservations')
@login_required
def view_reservations_route():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view reservations.')
        return redirect(url_for('auth.login'))
    
    user = UserDAO.get_user_by_id(user_id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    
    is_admin = user.username == 'admin'
    
    reservations = ReservationDAO.view_reservations(user.username, is_admin)
    return render_template('view_reservations.html', reservations=reservations, is_admin=is_admin, user=user)

# Route for reversing seats
@view_bp.route('/reverse_seats/<int:bus_id>/<int:seats_to_reverse>')
@login_required
def reverse_seats_route(bus_id, seats_to_reverse):
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to reverse seats.')
        return redirect(url_for('auth.login'))
    
    BusDAO.reverse_seats(bus_id, seats_to_reverse)
    return redirect(url_for('view.view_buses_route'))

# Route for buying a ticket
@view_bp.route('/buy_ticket/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def buy_ticket(bus_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to buy a ticket.')
        return redirect(url_for('auth.login'))
    
    user = UserDAO.get_user_by_id(current_user.id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    
    bus = BusDAO.get_bus(bus_id)
    if bus is None:
        flash('Bus not found.')
        return redirect(url_for('view.view_buses_route'))
    
    if request.method == 'POST':
        customer_name = user.username  # Use the username instead of customer_name from the form
        seats_reserved = int(request.form['seats_reserved'])
        plan = request.form['plan']
        
        if plan == 'block':
            total_price = 150  # Price for 1 block (~60 tickets)
        else:
            total_price = seats_reserved * bus.price  # Price for one-time tickets
        
        if user.balance < total_price:
            flash('Not enough balance to buy the ticket!')
            return redirect(url_for('view.buy_ticket', bus_id=bus_id))
        
        if ReservationDAO.make_reservation(bus_id, customer_name, seats_reserved, plan):
            UserDAO.update_balance(current_user.id, -total_price)  # Reduce the user's balance
            user = UserDAO.get_user_by_id(user_id)
            flash('Ticket purchased successfully!')
            # Generate QR code
            qr_data = f"Bus ID: {bus_id}, Customer: {customer_name}, Seats: {seats_reserved}, Plan: {plan}"
            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, 'PNG')
            buffer.seek(0)
            
            return redirect(url_for('view.my_tickets'))
        #send_file(buffer, mimetype='image/png', as_attachment=True, download_name='ticket_qr.png')
        else:
            flash('Not enough available seats!')
            return redirect(url_for('view.buy_ticket', bus_id=bus_id))
    
    return render_template('buy_ticket.html', bus=bus, user=user)

@view_bp.route('/generate_qr_code/<int:bus_id>/<customer_name>/<int:seats_reserved>')
@login_required
def generate_qr_code(bus_id, customer_name, seats_reserved):
    qr_data = f"Bus ID: {bus_id}, Customer: {customer_name}, Seats: {seats_reserved}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, 'PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

# Route for viewing user's tickets
@view_bp.route('/my_tickets')
@login_required
def my_tickets():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view your tickets.')
        return redirect(url_for('auth.login'))
    user = UserDAO.get_user_by_id(current_user.id)
    if user is None:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    is_admin = user.username == 'admin'
    reservations = ReservationDAO.view_reservations(user.username, is_admin)
    return render_template('my_tickets.html', reservations=reservations, is_admin=is_admin, user=user)

# Route for viewing and editing user profile
@view_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = UserDAO.get_user_by_id(user_id)
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        name = request.form['name']
        
        UserDAO.update_user(user_id, username, email, phone_number, gender, name)
        flash('Profile updated successfully!')
        return redirect(url_for('view.profile'))
    
    return render_template('profile.html', user=user)