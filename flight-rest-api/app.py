import json
from flask import Flask, request
from flask_restful import Resource, Api
from flask import Flask, jsonify, request
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

tickets = []