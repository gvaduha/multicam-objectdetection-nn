"""
Video capture module. Run capture from uri
Disabled:
  error E1101: Module 'cv2' has no 'VideoCapture' member [E:no-member]
"""
# pylint: disable=C0103,E1101,R0902

from threading import Thread
import cv2

class VideoCapture:
    """
    Mimicking emgucv VideoCapture wrapper
    If currentFrame returns grabbed == false than capture stops
    You can either check isRunning before call currentFrame or check currentFrame grabbed value
    """

    def __init__(self, vsid, uri, logger):
        """
        vsid: video source id that current image frame lable with
        uri: video source uri
        """
        self._logger = logger
        self.vsid = vsid
        self.uri = uri
        self._capture = cv2.VideoCapture(uri)
        self._grabbed = False
        self._frame = None
        self._started = False
        self._stopping = False

    def isRunning(self):
        """
        return if capture thread is running
        """
        return self._started

    def start(self):
        """
        start capture thread
        """
        if self._started:
            return self
        Thread(target=self._captureLoop, args=()).start()
        self._started = True
        self._logger.info(f'VideoCapture @{self.vsid}:{self.uri} started')
        return self

    def stop(self):
        """
        stop capture thread
        """
        if self._started:
            self._logger.info('VideoCapture stopping...')
            self._stopping = True
            self._started = False
            self._grabbed = False

    def _captureLoop(self):
        while not self._stopping:
            (self._grabbed, self._frame) = self._capture.read()
            if not self._grabbed:
                self.stop()
        self._logger.info(f'VideoCapture @{self.vsid}:{self.uri} stopped')

    def currentFrame(self):
        """
        return current image frame with video source id
        """
        return (self._grabbed, self._frame, self.vsid)
