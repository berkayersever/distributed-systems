import json
from flask import Flask, request
from flask_restful import Resource, Api

tickets = []


class Flight(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be left blank!")

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
