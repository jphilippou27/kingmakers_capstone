#! /bin/bash
PORT="${1:-8765}"
gunicorn --bind 0.0.0.0:$PORT --user=root --group=root wsgi\
    --keyfile /etc/letsencrypt/live/kingmakerscapstone.com/privkey.pem\
    --certfile /etc/letsencrypt/live/kingmakerscapstone.com/fullchain.pem

