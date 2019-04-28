from flask import Flask
from celery import Celery
from flask_socketio import SocketIO

async_mode = None  # 新添加的代码
socketio = SocketIO()


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    make_celery(app)

    from app.api.views import blue_hello
    app.register_blueprint(blue_hello)

    socketio.init_app(app=app, async_mode=async_mode, message_queue='amqp://')  # 新添加的代码
    return app
