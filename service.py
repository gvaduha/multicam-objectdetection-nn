"""
Main service module
"""
# pylint: disable=C0103,C0301,R0902

import threading
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
        self._detectorFree = True
        self._logger = logger
        self._initfromconfig(config)
        self._mainthread = threading.Thread(target=self._mainLoop, name='service')
        self._mainthread.start()

    def _initfromconfig(self, config):
        modulesconfig = config['modules']
        # Video sources
        self._cams = [VideoCapture(c['vsid'], c['uri'], self._logger) for c in config['cams']]
        self._logger.info(f"Video sources: {[f'{c.vsid}:{c.uri}' for c in self._cams]}")
        # Result subscriber
        self._detectionResultSubscriber = getattr(__import__(config['resultsink']['module']), config['resultsink']['class'])(modulesconfig.get(config['resultsink']['class'], None), self._logger)
        self._logger.info(f'Initialize result subscriber: {type(self._detectionResultSubscriber).__name__}')
        # Neural network
        nn = getattr(__import__(config['nn']['module']), config['nn']['class'])(modulesconfig.get(config['nn']['class'], None), self._logger)
        self._logger.info(f'Initialize neural network: {type(nn).__name__}')
        self._objDetector = ObjectDetector(nn, self._logger)

        self._runinterval = config['runintervalsec']
        self._logger.info(f"Service processing interval: {self._runinterval} sec")

        _ = [threading.Thread(target=c.start, name=f'vsid-{c.vsid}', args=()).start() for c in self._cams]

    def stop(self):
        """
        stops service loop
        """
        self._logger.info('Service stopping...')
        self._stopEvent = True
        self._objDetector.stop()
        self._detectionResultSubscriber.stop()
        for c in self._cams:
            c.stop()


    def _mainLoop(self):
        ticker = threading.Event()
        while not ticker.wait(self._runinterval) and not self._stopEvent:
            if self._detectorFree:
                self._detectionCycle()
            else:
                self._logger.warning('Detector is busy, skipping detection!')

        self._logger.info('Service stopped')

    def _detectionCycle(self):
        self._detectorFree = False
        for c in self._cams:
            if c.isRunning:
                (hasFrame, img, camid) = c.currentFrame()
            if hasFrame:
                frame = e.CapturedFrame(camid, dt.datetime.now(), img)
                self._objDetector.pushImage(frame)
            else:
                c = VideoCapture(c.vsid, c.uri, self._logger)
                threading.Thread(target=c.start, name=f'vsid-{c.vsid}', args=()).start()

        dset = self._objDetector.getDetectedObjectsFrame()
        self._detectionResultSubscriber.pushDetectedObjectsFrame(dset)
        self._detectorFree = True

    def join(self):
        """
        waits main event loop thread to return
        """
        self._mainthread.join()
