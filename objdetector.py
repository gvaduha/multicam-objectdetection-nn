#import numpy as np
import queue as q
import entities as e
from threading import Thread
from typing import List
import datetime as dt
import time

class ObjectDetector:
    """
    Facade to real object detection neural network
    nnclass argument should implement following interfact
     * detectObjects(frame: e.CapturedFrame) -> e.DetectedObjectSet
    """

    def __init__(self, nnclass):
        self._realnn = nnclass
        self._frames = q.Queue()
        self._stopSignal = False
        self._detectedObjectSets: List[e.DetectedObjectSet] = []
        Thread(target=self._detectObjectsLoop, args=()).start()

    def stop(self):
        self._stopSignal = True

    def _detectObjectsLoop(self):
        while(not self._stopSignal):
            try:
                frame:e.CapturedFrame = self._frames.get(timeout=1000)
                doset = self._realnn.detectObjects(frame)
                self._detectedObjectSets.append(doset)
            except q.Empty:
                pass

    def pushImage(self, frame: e.CapturedFrame):
        self._frames.put(frame)

    def getDetectedObjectsFrame(self) -> e.DetectedObjectsFrame:
        while(not self._frames.empty()):
            time.sleep(0.1)

        doframe = e.DetectedObjectsFrame("", dt.datetime.now(), self._detectedObjectSets)
        self._detectedObjectSets = []
        return doframe
