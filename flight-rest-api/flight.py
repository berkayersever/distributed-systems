import json, sqlite3
from flask import Flask, request
from flask_restful import Resource, reqparse, Api

tickets = []


class Flight(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank!")

    @classmethod
    def find_by_id(cls, flight_id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()
        query = "SELECT * FROM flights WHERE flight_id=?"
        result = cursor.execute(query, (flight_id,))
        row = result.fetchone()
        connection.close()
        if row:
            return {'flight': {'flight_id': row[0], 'to_where': row[1], 'from_where': row[2], 'date': row[3]}}

    def get(self, flight_id):
        flight = self.find_by_id(flight_id)
        if flight:
            return flight, 200
        return {'message': 'Flight not found'}, 404

    # def get(self):
    #     print("Get Request")
    #     data = (request.get_json())
    #     if 'PNR' not in data:
    #         return [{'PNR': 'a'}, {'PNR': 'b'}], 200
    #     if 'seat_number' in data:
    #         print("Seat number is already given.")
    #         print(data['seat_number'])
    #     PNR = data['PNR']
    #     if PNR in tickets:
    #         return request.get_json(), 200
    #     else:
    #         return {'message': 'Ticket not found'}, 404

    # def put(self):
    #     data = (request.get_json())
    #     PNR = data['PNR']
    #     tickets.append(PNR)
    #     return {'PNR':data['PNR']}, 201

    def put(self, name):
        data = Flight.parser.parse_args()
        item = next(filter(lambda x: x['name'] == name, items), None)
        if item is None:
            item = {'name': name, 'price': data['price']}
            items.append(item)
        else:
            item.update(data)
        return item


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
        return {'flights': flights}

    def put(self, name):