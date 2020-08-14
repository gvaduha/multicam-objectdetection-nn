from threading import Thread
import cv2

class VideoCapture:
    """
    Mimicking emgucv VideoCapture wrapper
    If currentFrame returns grabbed == false than capture stops
    You can either check isRunning before call currentFrame or check currentFrame grabbed value
    """

    def __init__(self, id, uri):
        self.id = id
        self.uri = uri
        self._capture = cv2.VideoCapture(uri)
        self._grabbed = False
        self._frame = None
        self._started = False
        self._stopping = False

    def isRunning():
        return self._started

    def start(self):
        if (self._started):
            return self
        Thread(target=self._captureLoop, args=()).start()
        self._started = True
        return self

    def stop(self):
        if (self._started):
            self._stopping = True
            self._started = False
            self._grabbed = False
    
    def _captureLoop(self):
        while not self._stopping:
            (self._grabbed, self._frame) = self._capture.read()
            if not self._grabbed:
                self.stop()

    def currentFrame(self):
        return (self._grabbed, self._frame, self.id)
