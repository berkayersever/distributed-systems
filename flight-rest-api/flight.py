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
            return {'flight': {'flight_id': row[0], 'to_where': row[1], 'from_where': row[2], 'date': row[3]}}

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
        query = "INSERT INTO flights VALUES (?, ?, ?, ?)"
        cursor.execute(query, (flight['flight_id'], flight['to_where'], flight['from_where'], flight['date']))
        connection.commit()
        connection.close()

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

    def put(self, flight_id):
        data = Flight.parser.parse_args()
        flight = self.find_by_id(flight_id)
        updated_flight = {'flight_id': flight_id, 'to_where': data['to_where'], 'from_where': data['from_where'], 'date': data['date']}
        if flight is None:
            try:
                self.insert(updated_flight)
            except RuntimeError:
                return {"message": "An error occurred while inserting the item."}, 500  # Internal Server Error
        else:
            try:
                self.update(updated_flight)
            except RuntimeError:
                return {"message": "An error occurred while updating the item."}, 500  # Internal Server Error
        return updated_flight


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
