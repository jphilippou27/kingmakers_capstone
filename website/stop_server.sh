#! /bin/bash

pgrep "gunicorn" | sudo xargs kill
