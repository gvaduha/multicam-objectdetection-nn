"""
Object detector facade module. Run object detection in NN
"""
# pylint: disable=C0103

#import numpy as np
from threading import Thread, Event
from typing import List
import datetime as dt
import time
import queue as q
import entities as e

class ObjectDetector:
    """
    Facade to real object detection neural network
    """

    def __init__(self, nnclass, logger):
        """
        nnclass argument should implement following interface
         * __init__(logger)
         * detectObjects(img) -> e.DetectedObjectSet
         * stop()
        """
        self._realnn = nnclass
        self._logger = logger
        self._frames = q.Queue()
        self._stopSignal = False
        self._processingEnabled = Event()
        self._processingEnabled.set()
        self._detectedObjectSets: List[e.DetectedObjectSet] = []
        Thread(target=self._detectObjectsLoop, args=()).start()
        self._logger.info('ObjectDetector started')

    def stop(self):
        """
        stops detection module
        """
        self._logger.info('ObjectDetector stopping...')
        self._stopSignal = True
        #self._processingEnabled.set()
        self._realnn.stop()

    def _detectObjectsLoop(self):
        while not self._stopSignal:
            try:
                frame: e.CapturedFrame = self._frames.get(timeout=1)
                self._processingEnabled.wait()
                dobjs = self._realnn.detectObjects(frame.img)
                doset = e.DetectedObjectSet(frame.vsid, frame.timestamp, dobjs)
                self._detectedObjectSets.append(doset)
            except q.Empty:
                pass
            except Exception as exc:
                self._logger.error(exc)

        self._logger.info('ObjectDetector stopped')

    def pushImage(self, frame: e.CapturedFrame):
        """
        push image into processing queue
        """
        self._frames.put(frame)

    def getDetectedObjectsFrame(self) -> e.DetectedObjectsFrame:
        """
        returns current list of all detected objects in DetectedObjectsFrame
        """
        self._processingEnabled.clear()
        while not self._frames.empty:
            time.sleep(0.1)

        doframe = e.DetectedObjectsFrame("", dt.datetime.now(), self._detectedObjectSets)
        self._detectedObjectSets = []
        self._processingEnabled.set()
        return doframe
