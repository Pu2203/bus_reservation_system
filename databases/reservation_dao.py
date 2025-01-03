import sqlite3

class ReservationDAO:
    @staticmethod
    def make_reservation(bus_id, username, customer_name, seats_reserved, plan):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT available_seats FROM buses WHERE id = ?', (bus_id,))
        available_seats = cursor.fetchone()[0]
        
        if available_seats < seats_reserved:
            conn.close()
            return False
        
        cursor.execute('''
            INSERT INTO tickets (bus_id, username, customer_name, seats_reserved, plan, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        ''', (bus_id, username, customer_name, seats_reserved, plan))
        
        cursor.execute('''
            UPDATE buses
            SET available_seats = available_seats - ?
            WHERE id = ?
        ''', (seats_reserved, bus_id))
        
        if available_seats == 0:
            cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
            
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def view_user_tickets(username, is_admin):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        if is_admin:
            cursor.execute('''
                SELECT tickets.id, buses.bus_number, buses.route, tickets.username, tickets.customer_name, tickets.seats_reserved, buses.time, buses.price, tickets.plan, tickets.status
                FROM tickets
                JOIN buses ON tickets.bus_id = buses.id
                JOIN users ON tickets.username = users.username
            ''')
        else:
            cursor.execute('''
                SELECT tickets.id, buses.bus_number, buses.route, tickets.username, tickets.customer_name, tickets.seats_reserved, buses.time, buses.price, tickets.plan, tickets.status
                FROM tickets
                JOIN buses ON tickets.bus_id = buses.id
                JOIN users ON tickets.username = users.username
                WHERE tickets.username = ?
            ''', (username,))
        
        tickets = cursor.fetchall()
        
        conn.close()
        return tickets
    
    @staticmethod
    def remove_ticket(ticket_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def update_ticket_status(ticket_id, status):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE tickets SET status = ? WHERE id = ?', (status, ticket_id))
        
        conn.commit()
        conn.close()