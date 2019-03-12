import json
from flask import Flask, request
from flask_restful import Resource, Api

tickets = []


class Flight(Resource):
    def get(self):
        print("Get Request")
        data = (request.get_json())
        if 'PNR' not in data:
            return [{'PNR': 'a'}, {'PNR': 'b'}], 200
        if 'seat_number' in data:
            print("Seat number is already given.")
            print(data['seat_number'])
        PNR = data['PNR']
        if PNR in tickets:
            return request.get_json(), 200
        else:
            return {'message': 'Ticket not found'}, 404

    def put(self):
        data = (request.get_json())
        PNR = data['PNR']
        tickets.append(PNR)
        return {'PNR':data['PNR']}, 201
