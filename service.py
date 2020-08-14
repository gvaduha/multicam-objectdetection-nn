from threading import Thread
from videocapture import VideoCapture
from objdetector import ObjectDetector
import entities as e
import datetime as dt

class Service:
    """
    Main app class with control loop
    """
    
    def __init__(self, config):
        self._stopEvent = False
        cams, objDetector = Service._init(config)
        self._mainthread = Thread(target=self._mainLoop, args=(cams, objDetector))
        self._mainthread.start()
    
    @staticmethod
    def _init(config):
        nn = getattr(__import__(config['nn']['module']), config['nn']['class'])()
        objDetector = ObjectDetector(nn)
        cams = [VideoCapture(c['id'],c['uri']) for c in config['cams']]
        [Thread(target=c.start, args=()).start() for c in cams]
        return (cams, objDetector)

    def stop():
        self._stopEvent = True

    def _mainLoop(self, cams, objDetector):
        while (not self._stopEvent):
            detectedObjects = []
            for c in cams:
                if (c.isRunning):
                    (hasFrame, img, camid) = c.currentFrame()
                if (hasFrame):
                    frame = e.CapturedFrame(camid, dt.datetime.now(), img)
                    objDetector.pushImage(frame)
                else:
                    c = VideoCapture(c.id, c.uri)
                    Thread(target=c.start, args=()).start()

            dset = objDetector.getDetectedObjectsFrame()
            print(dset)

    def join(self):
        self._mainthread.join()
