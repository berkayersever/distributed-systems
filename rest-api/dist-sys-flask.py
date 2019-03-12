from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello World!'


@app.route('/echo/<name>')
def text_echo(name):
    return 'hello {}'.format(name)


@app.route('/echo/<string:name>/<int:number>')
def text_echo_with_number(name, number):
    return 'hello{} - {}'.format(name, number*2)
