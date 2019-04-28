from app import create_app, socketio, make_celery
from flask_script import Manager, Shell

app = create_app()
celery = make_celery(app)
manager = Manager(app=app)


@manager.command
def runsocket():
    socketio.run(app=app, host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    manager.run()
