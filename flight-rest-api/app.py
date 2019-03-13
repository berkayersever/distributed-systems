import json
from flask import Flask, request
from flask_restful import Resource, Api
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource

from flight import Flight, FlightList, Ticket

app = Flask(__name__)
app.secret_key = "k8!vv3&m=g_p0-6w6do_&q05_6%ade5cs8^5*@zk=#kv16kd@+"
api = Api(app)

# tickets = []

api.add_resource(Flight, '/flight', '/flights/<int:flight_id>')
api.add_resource(FlightList, '/flights')
api.add_resource(Ticket, '/ticket')

if __name__ == '__main__':
    app.run(port=5000, debug=True, host='0.0.0.0')
