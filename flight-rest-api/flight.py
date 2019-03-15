import random, hashlib, time
import json, sqlite3
from flask import Flask, request
from flask_restful import Resource, reqparse, Api

tickets = []
secret_key = 'ZVmHVMt7mtqRg5E#vCjuFB29@P_QHaF6r5VmQH-dEhzHJ8YWmh'


def generate_pnr(length=10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    random.seed(hashlib.sha256(("%s%s%s" % (random.getstate(), time.time(), secret_key)).encode('utf-8')).digest())
    return ''.join(random.choice(allowed_chars) for i in range(length))


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

    # def get(self):
    #     connection = sqlite3.connect('data.db')
    #     cursor = connection.cursor()
    #     query = "SELECT * FROM flights"
    #     result = cursor.execute(query)
    #     flights = []
    #     for row in result:
    #         flights.append({'to_where': row[1], 'from_where': row[2], 'date': row[3], 'flight_id': row[0]})
    #     connection.close()
    #     return {'flights': flights}, 200

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

    def put(self):
        data = Flight.parser.parse_args()
        flight = {'to_where': data['to_where'], 'from_where': data['from_where'], 'date': data['date']}
        try:
            _id = self.insert(flight)
        except RuntimeError:
            return {"message": "An error occurred while inserting the item."}, 500  # Internal Server Error
        return {'flight_id': _id}, 201

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
    # parser.add_argument('seat_number', help="This field cannot be left blank!")
    parser.add_argument('flight_id', type=int, help="This field cannot be left blank!")
    print(parser)

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
        # print(row)
        # if row:
        #     data = {'flight': {'PNR': pnr, 'to_where': row[1], 'from_where': row[2], 'date': row[3], 'flight_id': row[0]}}


        # data = Flight.parser.parse_args()
        # flight = {'to_where': data['to_where'], 'from_where': data['from_where'], 'date': data['date']}

        cursor.execute("INSERT INTO tickets (PNR, flight_id, to_where, from_where, date) VALUES (?, ?, ?, ?, ?)", (pnr, ticket['flight_id'], row[1], row[2], row[3],))

        # cursor.execute("INSERT INTO tickets (PNR, flight_id) VALUES (?, ?)", (pnr, ticket['flight_id'],))
        connection.commit()
        connection.close()
        # return {'flight': {'to_where': row[1], 'from_where': row[2], 'date': row[3], 'flight_id': row[0]}}
        return {'PNR': pnr}

    @classmethod
    def find_by_id(cls, ticket):
        # print(type(ticket))
        # print(type(ticket['flight_id']))
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        _id = 'TK' + str(1900 + ticket['flight_id'])  # flight_id to be used in new table
        # print(_id)
        # query = "SELECT * FROM {} WHERE flight_id=?".format(_id)
        query = "SELECT * FROM flights WHERE flight_id=?"
        # result = cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date']))
        result = cursor.execute(query, (ticket['flight_id'],))
        row = result.fetchone()
        # print(row)
        connection.close()
        string = ticket['flight_id']
        # print("String: " + str(string))
        # print(str(ticket['flight_id'])[5:7])
        if row:
            # print(str(ticket['flight_id'])[5:7])
            return {'ticket': {'PNR': generate_pnr(), 'seat_number': 1, 'flight_id': ticket['flight_id']}}
            # return {'ticket': {'PNR': generate_pnr(), 'seat_number': 1, 'flight_id': row[0]}}

    @classmethod
    def find_by_pnr(cls, pnr):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        # print(pnr)
        # _id = 'TK' + str(1900 + ticket['flight_id'])  # flight_id to be used in new table

        query = "SELECT * FROM tickets WHERE PNR=?"
        # result = cursor.execute(query, (flight['to_where'], flight['from_where'], flight['date']))
        result = cursor.execute(query, (pnr,))


        # query = "SELECT * FROM {} WHERE flight_id=?".format(_id)
        # result = cursor.execute(query, (ticket['flight_id'],))
        row = result.fetchone()
        print(row)
        connection.close()
        if row:
            return {'ticket': {'to_where': row[2], 'from_where': row[3], 'date': row[4], 'flight_id': row[5], 'seat_number': 1}}


    # @classmethod
    # def find_by_pnr(cls, ticket):
    #     connection = sqlite3.connect('data.db')
    #     cursor = connection.cursor()
    #     _id = 'TK' + str(1900 + ticket['flight_id'])  # flight_id to be used in new table
    #     query = "SELECT * FROM {} WHERE flight_id=?".format(_id)
    #     result = cursor.execute(query, (ticket['flight_id'],))
    #     row = result.fetchone()
    #     connection.close()
    #     if row:
    #         return {'ticket': {'PNR': generate_pnr(), 'seat_number': 1, 'flight_id': row[0]}}

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

    def get_tickets(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM tickets"
        result = cursor.execute(query)
        flights = []
        for row in result:
            flights.append({'to_where': row[2], 'from_where': row[3], 'date': row[4], 'flight_id': row[5]})
        connection.close()
        return {'flights': flights}, 200




    # def get(self):
    #     data = Ticket.parser.parse_args()
    #     ticket = self.find_by_pnr(data['PNR'])
    #     if ticket:
    #         return ticket, 200
    #     return {'message': 'Flight not found'}, 404


    # def get(self, flight_id):
    #     ticket = self.find_by_id(flight_id)
    #     if ticket:
    #         return ticket, 200
    #     return {'message': 'Flight not found'}, 404

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
