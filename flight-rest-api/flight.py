import json, sqlite3
from flask import Flask, request
from flask_restful import Resource, reqparse, Api

tickets = []


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
            # return {'flight': {'flight_id': row[0], 'to_where': row[1], 'from_where': row[2], 'date': row[3]}}

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

class Ticket(Resource):
    parser = reqparse.RequestParser()
    # parser.add_argument('PNR', help="This field cannot be left blank!")
    # parser.add_argument('seat_number', help="This field cannot be left blank!")
    parser.add_argument('flight_id', type=int, help="This field cannot be left blank!")

    @classmethod
    def insert(cls, ticket):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        # query = "INSERT INTO tickets (PNR, seat_number, flight_id) VALUES (?, ?, ?)"
        query = "INSERT INTO tickets (flight_id) VALUES (?)"
        cursor.execute(query, (ticket['flight_id'],))
        connection.commit()
        connection.close()

    @classmethod
    def find_by_id(cls, ticket):
        # print(type(ticket))
        # print(type(ticket['flight_id']))
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM tickets WHERE flight_id=?"
        result = cursor.execute(query, (ticket['flight_id'],))
        row = result.fetchone()
        connection.close()
        if row:
            return {'ticket': {'PNR': 1000, 'seat_number': 1, 'flight_id': row[0]}}

    @classmethod
    def get_count(cls, ticket):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        ## query = "SELECT * FROM tickets WHERE flight_id=?"
        query = "SELECT count(*) FROM tickets WHERE flight_id=?"
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
            print("Hmm")
            print(self.get_count(ticket))
            if self.get_count(ticket) > 10:
                return {"message": "No seats are available"}, 409   # No Seats Left
            else:
                self.insert(ticket)
                return ticket, 200

    def get(self, flight_id):
        ticket = self.find_by_id(flight_id)
        if ticket:
            return ticket, 200
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
