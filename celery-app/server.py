import json
import time
from flask import Flask, jsonify
from celery import Celery

app = Flask(__name__)
app.config.update(
    broker_url='sqla+sqlite:///tasks_web.sqlite',
    result_backend='db+sqlite:///results_web.db'
)


def make_celery(app):
    """
    Require for Flask context, skip it
    """
    c = Celery(app.import_name, backend=app.config['result_backend'], broker=app.config['broker_url'])
    c.conf.update(app.config)
    TaskBase = c.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    c.Task = ContextTask
    return c


celery = make_celery(app)


@celery.task(name='server.registration')
def registration(email):
    with open('database.json', 'r') as db:
        items = json.loads(db.read())

    emails = [item['email'] for item in items]
    if email not in emails:
        items.append({'email': email})
        # perform other required operations, send email etc.
        time.sleep(10)
        with open('database.json', 'w') as db:
            db.write(json.dumps(items))
        return True

    return False


@app.route("/check/<t_id>")
def check(t_id):
    res = celery.AsyncResult(t_id)
    msg = jsonify(msg='Task has been completed!') if res.ready() else jsonify('Work in progress.')
    return msg


@app.route("/register/<email>")
def register(email):
    t = registration.delay(email)
    return jsonify({
        'msg': 'Your email will be registered in a short time.',
        'task': t.task_id
    })


@app.route("/login/<email>")
def login(email):
    with open('database.json', 'r') as db:
        items = json.loads(db.read())
        emails = [item['email'] for item in items]
    if email in emails:
        return jsonify({'msg': 'Success'})
    else:
        return jsonify({'msg': 'Access denied'})


if __name__ == '__main__':
    with open('database.json', 'w') as d:
        d.write(json.dumps([{'email': 'test@test.com'}]))
    app.run(debug=True)
