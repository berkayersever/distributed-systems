import random, hashlib, time
import json, sqlite3
from flask import Flask, request
from flask_restful import Resource, reqparse, Api
from flask_jwt import jwt_required, current_identity
import flask_jwt

tickets = []
secret_key = 'ZVmHVMt7mtqRg5E#vCjuFB29@P_QHaF6r5VmQH-dEhzHJ8YWmh'


def generate_pnr(length=10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    random.seed(hashlib.sha256(("%s%s%s" % (random.getstate(), time.time(), secret_key)).encode('utf-8')).digest())
    return ''.join(random.choice(allowed_chars) for i in range(length))


def generate_id(flight_id):
    return 'TK' + str(1900 + flight_id)


class Flight(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('to_where', help="This field cannot be left blank!")
    parser.add_argument('from_where', help="This field cannot be left blank!")
    parser.add_argument('date', help="This field cannot be left blank!")

    @classmethod
    def find_by_id(cls, flight):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM flights WHERE flight_id=?"
        result = cursor.execute(query, (flight,))
        row = result.fetchone()
        connection.close()
        if row:
            return {'flight': {'to_where': row[1], 'from_where': row[2], 'date': row[3], 'flight_id': row[0]}}

    @classmethod
    def update(cls, flight):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "UPDATE flights SET to_where=?, from_where=?, date=? WHERE flight_id=?"
        cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date'], flight['flight_id']))
        connection.commit()
        connection.close()

    @classmethod
    def insert(cls, flight):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "INSERT INTO flights (to_where, from_where, date) VALUES (?, ?, ?)"
        cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date']))

        query = "SELECT flight_id FROM flights WHERE to_where=? AND from_where=? AND date=?"
        result = cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date']))
        row = result.fetchone()
        _id = 'TK' + str(1900 + row[0])     # flight_id to be used in new table
        create_table = "CREATE TABLE IF NOT EXISTS {} (PNR TEXT UNIQUE, seat_number INTEGER DEFAULT 0, flight_id INTEGER DEFAULT {}, FOREIGN KEY (flight_id) REFERENCES flights(group_id))".format(_id, row[0])

        cursor.execute(create_table)
        connection.commit()
        connection.close()

    def delete(self, flight_id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        if not self.find_by_id(flight_id):
            return {'message': "A flight with id '{}' does not exist.".format(flight_id)}, 404
        query = "DELETE FROM flights WHERE flight_id=?"
        cursor.execute(query, (flight_id,))
        connection.commit()
        connection.close()
        return {'message': 'Flight deleted'}, 200

    def get(self, flight_id):
        flight = self.find_by_id(flight_id)
        if flight:
            return flight, 200
        return {'message': 'Flight not found'}, 404

    def post(self, flight_id):
        if self.find_by_id(flight_id):
            return {'message': "A flight with id '{}' already exists.".format(flight_id)}, 400
        data = Flight.parser.parse_args()
        flight = {'flight_id': flight_id, 'to_where': data['to_where'],
                  'from_where': data['from_where'], 'date': data['date']}
        try:
            self.insert(flight)
        except RuntimeError:
            return {"message": "An error occurred while inserting the flight."}, 500  # Internal Server Error
        return flight, 201

    def put(self):
        data = Flight.parser.parse_args()
        flight = {'to_where': data['to_where'], 'from_where': data['from_where'], 'date': data['date']}
        try:
            self.insert(flight)
        except RuntimeError:
            return {"message": "An error occurred while inserting the item."}, 500  # Internal Server Error
        return flight, 201


class FlightList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('to_where', help="This field cannot be left blank!")
    parser.add_argument('from_where', help="This field cannot be left blank!")
    parser.add_argument('date', help="This field cannot be left blank!")

    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM flights"
        result = cursor.execute(query)
        flights = []
        for row in result:
            flights.append({'to_where': row[1], 'from_where': row[2], 'date': row[3], 'flight_id': row[0]})
        connection.close()
        return {'flights': flights}, 200

    @jwt_required()
    def put(self):
        user = current_identity
        if user.username == 'admin':
            data = Flight.parser.parse_args()
            flight = {'to_where': data['to_where'], 'from_where': data['from_where'], 'date': data['date']}
            try:
                _id = self.insert(flight)
            except RuntimeError:
                return {"message": "An error occurred while inserting the item."}, 500  # Internal Server Error
            return {'flight_id': _id}, 201
        else:
            return {'message': 'Authorization Required'}, 401

    @classmethod
    def insert(cls, flight):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "INSERT INTO flights (to_where, from_where, date) VALUES (?, ?, ?)"
        cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date']))
        query = "SELECT flight_id FROM flights WHERE to_where=? AND from_where=? AND date=?"
        result = cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date']))
        row = result.fetchone()
        _id = 'TK' + str(1900 + row[0])  # flight_id to be used in new table
        create_table = "CREATE TABLE IF NOT EXISTS {} (PNR TEXT UNIQUE, seat_number INTEGER DEFAULT 0, flight_id INTEGER DEFAULT {}, FOREIGN KEY (flight_id) REFERENCES flights(group_id))".format(_id, row[0])
        cursor.execute(create_table)
        connection.commit()
        connection.close()
        return _id


class Ticket(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('PNR')
    parser.add_argument('seat_number', type=int)
    parser.add_argument('flight_id', type=int, help="This field cannot be left blank!")

    @classmethod
    def insert(cls, ticket):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        _id = 'TK' + str(1900 + ticket['flight_id'])  # flight_id to be used in new table
        query = "INSERT INTO {} (PNR, flight_id) VALUES (?, ?)".format(_id)
        pnr = generate_pnr()
        cursor.execute(query, (pnr, ticket['flight_id'],))
        query = "SELECT * FROM flights WHERE flight_id=?"
        result = cursor.execute(query, (ticket['flight_id'],))
        row = result.fetchone()
        cursor.execute("INSERT INTO tickets (PNR, flight_id, to_where, from_where, date) VALUES (?, ?, ?, ?, ?)", (pnr, ticket['flight_id'], row[1], row[2], row[3],))
        connection.commit()
        connection.close()
        return {'PNR': pnr}

    @classmethod
    def find_by_id(cls, ticket):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        _id = 'TK' + str(1900 + ticket['flight_id'])  # flight_id to be used in new table
        query = "SELECT * FROM flights WHERE flight_id=?"
        result = cursor.execute(query, (ticket['flight_id'],))
        row = result.fetchone()
        connection.close()
        if row:
            return {'ticket': {'PNR': generate_pnr(), 'seat_number': ticket['seat_number'], 'flight_id': ticket['flight_id']}} # Seat Number is not needed probably

    @classmethod
    def find_by_pnr(cls, pnr):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM tickets WHERE PNR=?"
        result = cursor.execute(query, (pnr,))
        row = result.fetchone()
        connection.close()
        if row:
            return {'to_where': row[2], 'from_where': row[3], 'date': row[4], 'flight_id': row[5], 'seat_number': row[1]} # Seat number is not needed probably
            # return {'ticket': {'to_where': row[2], 'from_where': row[3], 'date': row[4], 'flight_id': row[5], 'seat_number': 1}} # Alternative Format

    @classmethod
    def get_count(cls, ticket):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        _id = 'TK' + str(1900 + ticket['flight_id'])  # flight_id to be used in new table
        query = "SELECT count(*) FROM {} WHERE flight_id=?".format(_id)
        result = cursor.execute(query, (ticket['flight_id'],))
        row = result.fetchone()
        connection.close()
        if row:
            return row[0]

    def put(self):
        data = Ticket.parser.parse_args()
        ticket = {'flight_id': data['flight_id']}
        # ticket = self.find_by_id()
        if not self.find_by_id(ticket):
            return {"message": "Flight ID does not exist"}, 404     # Not Found
        else:
            if self.get_count(ticket) > 99:
                return {"message": "No seats are available"}, 409   # No Seats Left
            else:
                return self.insert(ticket), 200

    def get(self):
        try:
            data = Ticket.parser.parse_args()
            ticket = self.find_by_pnr(data['PNR'])
            if ticket:
                return ticket, 200
            return {'message': 'Flight not found'}, 404
        except Exception as e:
            return self.get_tickets()

    @jwt_required()
    def get_tickets(self):
        user = current_identity
        if user.username == 'admin':
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "SELECT * FROM tickets"
            result = cursor.execute(query)
            flights = []
            for row in result:
                flights.append({'to_where': row[2], 'from_where': row[3], 'date': row[4], 'flight_id': row[5]})
            connection.close()
            return {'flights': flights}, 200
        else:
            return {'message': 'Authorization Required'}, 401

    def post(self):
        data = Ticket.parser.parse_args()
        ticket = {'PNR': data['PNR']}
        temp = self.find_by_pnr(ticket['PNR'])
        if temp:
            connection = sqlite3.connect('data.db')
            cursor = connection.cursor()
            query = "SELECT count(*) FROM tickets WHERE seat_number=? AND flight_id=?"
            result = cursor.execute(query, (data['seat_number'], temp['flight_id'],))
            row = result.fetchone()
            if row[0] == 0:
                query = "UPDATE tickets SET seat_number =? WHERE PNR=?"
                cursor.execute(query, (data['seat_number'], ticket['PNR'],))
                connection.commit()
                connection.close()
                return {'PNR': ticket['PNR'], 'seat_number': data['seat_number']}, 200
            else:
                connection.close()
                return {'message': "Seat number {} is not available for {}.".format(data['seat_number'], generate_id(temp['flight_id']))}, 409  # Seat Not Available
        else:
            return {'message': "PNR: {} does not exist".format(ticket['PNR'])}, 404    # PNR Not Found

    def delete(self):
        data = Ticket.parser.parse_args()
        ticket = {'PNR': data['PNR']}
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM tickets WHERE PNR=?"
        result = cursor.execute(query, (ticket['PNR'],))
        row = result.fetchone()
        if row:
            query = "DELETE FROM tickets WHERE PNR=?"
            cursor.execute(query, (ticket['PNR'],))
            connection.commit()
            connection.close()
            return {'message': "Ticket with PNR: {} has been cancelled".format(ticket['PNR'])}, 200  # Cancel Ticket
        else:
            connection.close()
            return {'message': "PNR: {} does not exist".format(ticket['PNR'])}, 404  # PNR Not Found
