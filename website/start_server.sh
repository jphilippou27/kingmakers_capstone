#! /bin/bash
gunicorn --bind 0.0.0.0:8765 --daemon --user=root --group=root wsgi
