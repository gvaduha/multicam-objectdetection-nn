"""
Flask result sink app
thanks to Kostas Pelelis for flask wrappers idea
(https://stackoverflow.com/questions/40460846/using-flask-inside-class)
"""
# pylint: disable=C0103,C0301,R0903

import json
import threading
from multiprocessing import Process, Queue, Event
from flask import Flask, Response

import entities as e

class EndpointAction:
    """
    Endpoint wrapper
    """
    def __init__(self, action):
        self._action = action
        self._response = Response(status=200, headers={'Content-Type': 'application/json'})

    def __call__(self, *args):
        self._action(self._response)
        return self._response

class FlaskApp:
    """
    Flask _app wrapper and implementation of SinkResult interface
    """
    def __init__(self):
        self._app = None
        self._currentresult = {}
        self._interprocq = None
        self._lock = None

    def addEndpoint(self, endpoint, handler):
        """
        Add enpoint
        """
        self._app.add_url_rule(endpoint, endpoint, EndpointAction(handler))

    def _resultep(self, resp):
        self._lock.acquire()
        res = self._currentresult
        self._lock.release()
        resp.data = json.dumps(res, cls=e.EntitiesJsonSerializer)

    def run(self, config: str, queue: Queue, ready: Event):
        """
        Start fuction for a process
        initialization of flask app should be here, trying initialize it
        in __init__ raise weird pickle serialization exception, python is so pyhton
        """
        self._app = Flask(type(self).__name__)
        self._app.use_reloader = False # to not run on main thread
        self.addEndpoint('/currentresult', self._resultep)
        self._interprocq = queue
        self._lock = threading.Lock()
        threading.Thread(target=self._flaskAppResultFeatThread).start()
        srv = config.get('server', 'localhost:5000').split(':')
        ready.set()
        self._app.run(host=srv[0], port=srv[1])


    def _flaskAppResultFeatThread(self):
        while True:
            res = self._interprocq.get()
            self._lock.acquire()
            self._currentresult = res
            self._lock.release()


class FlaskResultSink:
    """
    Implementation of SinkResult interface that sends data to FlaskApp
    """
    def __init__(self, config, logger):
        self._logger = logger
        self._config = config
        self._interprocq = Queue()
        readyflag = Event()
        self._flaskproc = Process(target=FlaskApp().run, args=(self._config, self._interprocq, readyflag))
        #self._flaskproc.daemon = True
        self._flaskproc.start()
        readyflag.wait(timeout=5)

    def stop(self):
        """
        Stop flask app
        """
        self._flaskproc.terminate()

    def pushDetectedObjectsFrame(self, frame: e.DetectedObjectsFrame):
        """
        Implementation of SinkResult interface
        """
        self._interprocq.put(frame)
