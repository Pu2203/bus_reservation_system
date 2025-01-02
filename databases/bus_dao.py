import sqlite3
from website.models import Bus

class BusDAO:
    @staticmethod
    def add_bus(bus_number, route, total_seats, time, price):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO buses (bus_number, route, total_seats, available_seats, time, price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bus_number, route, total_seats, total_seats, time, price))
        conn.commit()
        conn.close()

    @staticmethod
    def view_buses(sort_by=None, search_query=None):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        query = 'SELECT * FROM buses'
        params = []
        
        if search_query:
            query += ' WHERE route LIKE ?'
            params.append(f'%{search_query}%')
        
        if sort_by:
            query += f' ORDER BY {sort_by}'
        
        cursor.execute(query, params)
        buses_data = cursor.fetchall()
        
        conn.close()
        
        buses = []
        for bus_data in buses_data:
            buses.append(Bus(
                id=bus_data[0],
                bus_number=bus_data[1],
                route=bus_data[2],
                total_seats=bus_data[3],
                available_seats=bus_data[4],
                time=bus_data[5],
                price=bus_data[6]
            ))
        return buses

    @staticmethod
    def get_bus(bus_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
        bus_data = cursor.fetchone()
        
        conn.close()
        
        if bus_data:
            return Bus(
                id=bus_data[0],
                bus_number=bus_data[1],
                route=bus_data[2],
                total_seats=bus_data[3],
                available_seats=bus_data[4],
                time=bus_data[5],
                price=bus_data[6]
            )
        return None

    @staticmethod
    def update_bus(bus_id, bus_number, route, total_seats, available_seats, time, price):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE buses
            SET bus_number = ?, route = ?, total_seats = ?, available_seats = ?, time = ?, price = ?
            WHERE id = ?
        ''', (bus_number, route, total_seats, available_seats, time, price, bus_id))
        
        conn.commit()
        conn.close()

    @staticmethod
    def delete_bus_from_db(bus_id):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
        
        conn.commit()
        conn.close()

    @staticmethod
    def reverse_seats(bus_id, seats_to_reverse):
        conn = sqlite3.connect('bus_reservation.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE buses
            SET available_seats = available_seats + ?
            WHERE id = ?
        ''', (seats_to_reverse, bus_id))
        
        cursor.execute('SELECT available_seats FROM buses WHERE id = ?', (bus_id,))
        available_seats = cursor.fetchone()[0]
        
        if available_seats == 0:
            cursor.execute('DELETE FROM buses WHERE id = ?', (bus_id,))
        
        conn.commit()
        conn.close()