#!/usr/bin/env bash
#--------------------------------------------
# celery -A manage.celery worker --loglevel=info &
# python manage.py runsocket
#--------------------------------------------


supervisord -c supervisor.conf