from gevent import monkey

monkey.patch_all()

import time
from threading import Thread
import project_blueprints
from flask import Flask
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
import utils.specs as project_vars
from timing_task import timing_task

app = project_blueprints.bind_blueprints(Flask(__name__, static_folder="", static_url_path=None))
app.url_map.default_subdomain = ''
app.config.update({
    'SERVER_NAME': project_vars.DOMAIN,
    'DEBUG': 'False'
})
app.debug = False

print(app.url_map)

http_server = WSGIServer(('45.76.102.168', 80), app, handler_class=WebSocketHandler)


def start():
    http_server.serve_forever()


tr = Thread(target=start)
tr.start()

while 1:
    timing_task.check()
    time.sleep(timing_task.check_interval)
