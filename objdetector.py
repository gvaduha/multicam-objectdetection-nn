#import numpy as np
import queue as q
import entities as e
from threading import Thread
from typing import Queue

class ObjectDetector:
    """
    Facade to real object detection neural network
    nnclass argument should implement following interfact
     * detectObjects(frame: e.CapturedFrame) -> e.DetectedObjectSet
    """

    def __init__(self, nnclass):
        self._realnn = nnclass
        self._frames:Queue[e.CapturedFrame] = q.Queue()
        self._t = Thread(target=self._detectObjectsLoop, args=()).start()
        self._stopSignal = False


    def _detectObjectsLoop(self):
        while(not self._stopSignal):
            img = self._frames.get(timeout=1000)
            if (img):
                doset = self._realnn.detectObjects(img.)
                print(doset)

    def pushImage(self, frame: e.CapturedFrame):
        self._frames.put(frame)

    def getDetectedSet() -> e.DetectedObjectSet:
        return None
