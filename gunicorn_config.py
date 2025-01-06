# gunicorn_config.py
workers = 1
timeout = 120
bind = "0.0.0.0:10000"
capture_output = True
loglevel = "info"