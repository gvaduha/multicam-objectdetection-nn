from threading import Thread
from videocapture import VideoCapture
from objdetector import ObjectDetector
import json
import datetime as dt
import signal

stopSignal = False

def stopHandler(signum, frame):
    print('Stopping...')
    stopSignal = True


def init(config):
    nn = getattr(__import__(config['nn']['module']), config['nn']['class'])()
    objDetector = ObjectDetector(nn)
    cams = [VideoCapture(c['id'],c['uri']) for c in config['cams']]
    [Thread(target=c.start, args=()).start() for c in cams]
    return (cams, objDetector)

def mainLoop(cams, nn):
    while (not stopSignal):
        detectedObjects = []
        for c in cams:
            timestamp = dt.datetime.now()
            if (c.isRunning):
                (hasFrame, frame, camid) = c.currentFrame()
            if (hasFrame):
                nn.pushImage(frame)
            else:
                c = VideoCapture(c.id, c.uri)
                Thread(target=c.start, args=()).start()

        dset = nn.getDetectedSet()
        #print(detectedObjects)


def main():
    with open('config.json') as cfgfile:
        config = json.load(cfgfile)

    (cams, nn) = init(config)
    mainthread = Thread(target=mainLoop, args=(cams, nn))

    print('Press ctrl-c to stop')
    mainthread.start()
    mainthread.join()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stopHandler)
    main()
