#! /bin/bash
PORT="${1:-8765}"
gunicorn --bind 0.0.0.0:$PORT --daemon --user=root --group=root wsgi
