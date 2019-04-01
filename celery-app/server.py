from flask import Flask
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
