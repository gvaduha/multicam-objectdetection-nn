"""
Main service module
"""
# pylint: disable=C0103, C0301

from threading import Thread
from videocapture import VideoCapture
from objdetector import ObjectDetector
import datetime as dt
import entities as e

class Service:
    """
    Main app class with control loop
    """

    def __init__(self, config):
        """
        Class initialization. Automatically starts event service loop thread as its last statement
        config: json for instantiation of neural network and detection results sink classes
        """
        self._stopEvent = False
        cams, objDetector, detectionResultSubscriber = Service._init(config)
        self._mainthread = Thread(target=self._mainLoop, args=(cams, objDetector, detectionResultSubscriber))
        self._mainthread.start()

    @staticmethod
    def _init(config):
        nn = getattr(__import__(config['nn']['module']), config['nn']['class'])()
        detectionResultSubscriber = getattr(__import__(config['resultsink']['module']), config['resultsink']['class'])()
        objDetector = ObjectDetector(nn)
        cams = [VideoCapture(c['id'], c['uri']) for c in config['cams']]
        _ = [Thread(target=c.start, args=()).start() for c in cams]
        return (cams, objDetector, detectionResultSubscriber)

    def stop(self):
        """
        stops service loop
        """
        self._stopEvent = True

    def _mainLoop(self, cams, objDetector, detectionResultSubscriber):
        while not self._stopEvent:
            for c in cams:
                if c.isRunning:
                    (hasFrame, img, camid) = c.currentFrame()
                if hasFrame:
                    frame = e.CapturedFrame(camid, dt.datetime.now(), img)
                    objDetector.pushImage(frame)
                else:
                    c = VideoCapture(c.vsid, c.uri)
                    Thread(target=c.start, args=()).start()

            dset = objDetector.getDetectedObjectsFrame()
            detectionResultSubscriber.pushDetectedObjectsFrame(dset)

    def join(self):
        """
        waits main event loop thread to return
        """
        self._mainthread.join()
