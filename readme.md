gunicorn + eventlet 

    gunicorn --worker-class eventlet -w 1 manage:app

gunicorn gevent

    gunicorn -k gevent -w 1 manage:app
    gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 manage:app 

uwsgi

    # uwsgi --http :5000 --gevent 10 --http-websockets --master --module manage:app
    uwsgi --http :5000 --http-websockets --master --module manage:app