#!/bin/bash

cd "$(dirname "$0")"

[ "x$APP_WORKERS" = "x" ] && export APP_WORKERS="1"
[ "x$APP_BIND" = "x" ] && export APP_BIND="0.0.0.0"
[ "x$APP_PORT" = "x" ] && export APP_PORT="5000"

gunicorn \
  --workers=$APP_WORKERS \
  --bind=${APP_BIND}:${APP_PORT} \
  --log-level=info \
  --error-logfile=/dev/stderr \
  --access-logfile=/dev/stdout \
  --log-file=/dev/stdout \
  wsgi:app
