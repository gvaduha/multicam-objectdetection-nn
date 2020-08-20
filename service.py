"""
Main service module
"""
# pylint: disable=C0103, C0301

import threading
import time
import datetime as dt

from videocapture import VideoCapture
from objdetector import ObjectDetector
import entities as e

class Service:
    """
    Main app class with control loop
    """

    def __init__(self, config, logger):
        """
        Class initialization. Automatically starts event service loop thread as its last statement
        config: json for instantiation of neural network and detection results sink classes
        """
        self._stopEvent = False
        self._logger = logger
        self._initfromconfig(config)
        self._mainthread = threading.Thread(target=self._mainLoop)
        self._mainthread.start()

    def _initfromconfig(self, config):
        nn = getattr(__import__(config['nn']['module']), config['nn']['class'])(self._logger)
        self._logger.debug(f'Initialize neural network: {type(nn).__name__}')
        self._objDetector = ObjectDetector(nn, self._logger)

        self._detectionResultSubscriber = getattr(__import__(config['resultsink']['module']), config['resultsink']['class'])(self._logger)
        self._logger.debug(f'Initialize result subscriber: {type(self._detectionResultSubscriber).__name__}')

        self._cams = [VideoCapture(c['vsid'], c['uri'], self._logger) for c in config['cams']]
        self._logger.debug(f"Video sources: {[f'{c.vsid}:{c.uri}' for c in self._cams]}")

        self._runinterval = config['runintervalsec'];
        self._logger.debug(f"Service processing interval: {self._runinterval} sec")

        _ = [threading.Thread(target=c.start, args=()).start() for c in self._cams]

    def stop(self):
        """
        stops service loop
        """
        self._logger.debug('Service stopping...')
        self._stopEvent = True
        self._objDetector.stop()
        self._detectionResultSubscriber.stop()
        for c in self._cams:
            c.stop()


    def _mainLoop(self):
        ticker = threading.Event()
        while not ticker.wait(self._runinterval) and not self._stopEvent:
            self._detectionCycle()
        self._logger.debug('Service stopped')

    def _detectionCycle(self):
        for c in self._cams:
            if c.isRunning:
                (hasFrame, img, camid) = c.currentFrame()
            if hasFrame:
                frame = e.CapturedFrame(camid, dt.datetime.now(), img)
                self._objDetector.pushImage(frame)
            else:
                c = VideoCapture(c.vsid, c.uri, self._logger)
                threading.Thread(target=c.start, args=()).start()

        dset = self._objDetector.getDetectedObjectsFrame()
        self._detectionResultSubscriber.pushDetectedObjectsFrame(dset)

    def join(self):
        """
        waits main event loop thread to return
        """
        self._mainthread.join()
