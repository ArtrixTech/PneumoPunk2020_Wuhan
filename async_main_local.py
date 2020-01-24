from gevent import monkey

monkey.patch_all()

import time
from threading import Thread
import project_blueprints
from flask import Flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import utils.specs as project_vars

app = project_blueprints.bind_blueprints(
    Flask(__name__, static_folder="", static_url_path=None))
app.url_map.default_subdomain = ''
app.config.update({
    'SERVER_NAME': project_vars.LOCAL_DOMAIN,
    'DEBUG': 'True'
})
app.debug = True

print(app.url_map)

# Local IP Address
http_server = WSGIServer(('127.0.0.1', 80), app,
                         handler_class=WebSocketHandler)


def start():
    http_server.serve_forever()


tr = Thread(target=start)
tr.start()

while True:
    time.sleep(10)
