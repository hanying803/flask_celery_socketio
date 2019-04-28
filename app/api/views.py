import psutil
from flask import Blueprint
from flask import render_template
from app.tasks.tasks import say_hi
from app.tasks.tasks import long_task
from app import socketio
import time
from threading import Lock
from flask import jsonify
import eventlet
eventlet.monkey_patch()

blue_hello = Blueprint('hello', __name__)
thread = None
thread_lock = Lock()


@blue_hello.route('/')
def index():
    say_hi.delay()
    return render_template("index.html")


@blue_hello.route('/sys/')
def sys_cup():
    return render_template('sys_cpu.html', async_mode=socketio.async_mode)


@blue_hello.route('/task/hi/')
def hi():
    task_id = say_hi.delay()
    return task_id.id


from celery.app import app_or_default

celery_app = app_or_default()


@celery_app.task
def long_task2():
    print('OK')
    socketio.emit('echo', '已收到', namespace='/test')
    count = 0
    while 1:
        count += 1
        time.sleep(10)
        if count > 100:
            break
        print(count)
        socketio.emit('echo', '{}'.format(count), namespace='/test')


@blue_hello.route('/task/long_task/')
def start_long_task():
    # socketio.start_background_task(target=long_task.apply_async)
    task_id = long_task2.delay()
    return render_template('task_status.html')


@blue_hello.route('/status/<task_id>')
def taskstatus(task_id):
    task = say_hi.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


# 后台线程 产生数据，即刻推送至前端
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(5)
        count += 1
        t = time.strftime('%M:%S', time.localtime())  # 获取系统时间（只取分:秒）
        cpus = psutil.cpu_percent(interval=None, percpu=True)  # 获取系统cpu使用率 non-blocking
        socketio.emit('server_response',
                      {'data': [t, *cpus], 'count': count},
                      namespace='/test')  # 注意：这里不需要客户端连接的上下文，默认 broadcast = True ！！！！！！！


# @socketio.on('connect', namespace='/test')
# def test_connect():
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(target=background_thread)

@socketio.on('connect', namespace='/test')
def test_connect():
    socketio.emit('my response', {'data': 'Connected'})
    socketio.emit('my response', {'data': 'Connected'}, namespace='/test')


@socketio.on('message', namespace='/test')
def handle_message(message):
    print('received message: ' + message)
    socketio.emit('echo', '已收到' + message, namespace='/test')
    socketio.emit('echo', '2已收到' + message)
