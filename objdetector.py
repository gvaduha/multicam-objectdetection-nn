"""
Object detector facade module. Run object detection in NN
"""
# pylint: disable=C0103,C0301,W0703,R0903

#import numpy as np
from threading import Thread, Event, Lock
from typing import List
import datetime as dt
import copy
import queue as q
import entities as e

class QueueSeparator:
    """
    Separator in queue show that block of images for slice of time has completed
    """

class ObjectDetector:
    """
    Facade to real object detection neural network
    """

    def __init__(self, nnclass, logger):
        """
        nnclass argument should implement following interface
         * __init__(logger)
         * detectObjects(img) -> List[e.DetectedObject]
         * stop()
        """
        self._realnn = nnclass
        self._logger = logger
        self._frames = q.Queue()
        self._stopSignal = False
        self._imgSetEnded = Event()
        self._lock = Lock()
        self._detectedObjectSets: List[e.DetectedObjectSet] = []
        Thread(target=self._detectObjectsLoop, name='objdetector', args=()).start()
        self._logger.info('ObjectDetector started')

    def stop(self):
        """
        stops detection module
        """
        self._logger.info('ObjectDetector stopping...')
        self._stopSignal = True
        self._imgSetEnded.set()
        self._realnn.stop()

    def _detectObjectsLoop(self):
        while not self._stopSignal:
            try:
                frame = self._frames.get(block=False)
                if isinstance(frame, QueueSeparator):
                    self._imgSetEnded.set()
                    continue
                self._imgSetEnded.clear()
                self._logger.debug(f'Infer from vsid:{frame.vsid}')
                rgbimg = frame.img[:, :, [2, 1, 0]]  # BGR2RGB
                dobjs = self._realnn.detectObjects(rgbimg)
                doset = e.DetectedObjectSet(frame.vsid, frame.timestamp, dobjs)
                self._lock.acquire()
                self._detectedObjectSets.append(doset)
                self._lock.release()
            except q.Empty:
                continue
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
        self._frames.put(QueueSeparator())
        self._imgSetEnded.wait()

        self._lock.acquire()
        doframe = e.DetectedObjectsFrame("", dt.datetime.now(), copy.deepcopy(self._detectedObjectSets))
        self._detectedObjectSets = []
        self._lock.release()

        return doframe

    @staticmethod
    def getDetectedObjectsCollection(nnout, hscale, wscale, threshold, tlbr=True) -> List[e.DetectedObject]:
        """
        Static helper
        Transforms network output to DetectedObject list
        nnout should be: (classes, scores, bboxes)
        NOTE! by default boxes have to be in (t,l,b,r) coordinate sequence
              if they're not set tlbr=False and parse as (l,t,r,b)
        """
        dobjs: List[e.DetectedObject] = []

        for c, s, bb in nnout:
            if s < threshold:
                break
            if tlbr:
                # transform (l,t,b,r) -> (t,l,r,b)
                bbox = e.BoundingBox(int(bb[1]*hscale), int(bb[0]*wscale), int(bb[3]*hscale), int(bb[2]*wscale))
            else:
                # transform (t,l,r,b) -> (t,l,r,b)
                bbox = e.BoundingBox(int(bb[0]*wscale), int(bb[1]*hscale), int(bb[2]*wscale), int(bb[3]*hscale))
            dobjs.append(e.DetectedObject(int(c), round(float(s), 2), bbox))

        return dobjs
