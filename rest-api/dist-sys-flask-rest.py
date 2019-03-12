from flask import Flask, requests
from flask_restful import

app = Flask(__name__)

class HelloWorld(Resource):
    def get(self):
        return json.dumps({'secret':'value'})

class TodoSimple(Resource):
    def get(self, todo_id):
        item = todos.get(todo_id, {})
        if not item:
            return item, 404
        return json.dumps({})