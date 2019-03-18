import json
from flask import Flask, request
from flask_restful import Resource, Api
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource
from flask_jwt import JWT

from create_tables import create_tables
from flight import Flight, FlightList, Ticket
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = "k8!vv3&m=g_p0-6w6do_&q05_6%ade5cs8^5*@zk=#kv16kd@+"       # Secret Key
api = Api(app)

# tickets = []
jwt = JWT(app, authenticate, identity)                                      # /auth

api.add_resource(Flight, '/flights/<int:flight_id>')
api.add_resource(FlightList, '/flights')
api.add_resource(Ticket, '/ticket')

if __name__ == '__main__':
    create_tables()
    app.run(port=5000, debug=True, host='0.0.0.0')
