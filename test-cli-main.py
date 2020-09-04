"""
Simple client to show results of the detection
"""

import sys
import traceback
import threading
import json
import requests
import cv2

"""
Hardcoded constants:
Interval for update detected objects
Minimal object score to display box
Ignored classes to hide from display
"""
UpdateDetectionDataInterval = 1.0
MinScore = 0.3
IgnoreClasses = [6,7]

class Program:
    def __init__(self):
        self._currentObjects = []
        self._lock = threading.RLock()
        self._stopping = False


    def _getColor(self, n):
        r,g,b = '{0:03b}'.format(n)[-3:4]
        return (255-int(r)*128, 255-int(g)*128, 255-int(b)*128)

    def _getCurrentObjects(self, vsid, datauri):
        """
        Get detected object collection from datauri
        """
        try:
            if not self._stopping:
                resp = requests.get(datauri)
                if resp.status_code == 200:
                    data = json.loads(resp.content.decode('utf-8'))
                    if data:
                        # python is pain-in-the-ass, doing ad-hock
                        vsdata = next((x for x in data['dsets'] if int(x['vsid']) == int(vsid)), None)
                        if vsdata:
                            objs = [(x['c'], x['p'], (x['bbox']['l'], x['bbox']['t']), (x['bbox']['r'], x['bbox']['b'])) for x in vsdata['dobjs'] if float(x['p']) >= MinScore and int(x['c'] not in IgnoreClasses)]
                            self._lock.acquire()
                            self._currentObjects = objs
                            self._lock.release()
                            print(f'Pumped data {self._currentObjects}')
                else:
                    print(f'Service retured error {resp.status_code}')
            else:
                print('Stopping data pump thread')
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
        finally:
            if not self._stopping:
                threading.Timer(UpdateDetectionDataInterval, self._getCurrentObjects, args=(vsid, datauri)).start()


    def main(self, vsid, vsuri, datauri):
        """
        Main function
        """
        print(f'Capturing {vsuri} with data from {datauri}')
        try:
            self._getCurrentObjects(vsid, datauri)
            wndname = f'**ESC to STOP** [{vsuri}] '
            cv2.namedWindow(wndname, cv2.WINDOW_NORMAL)
            cam = cv2.VideoCapture(vsuri)
            while True:
                ret, img = cam.read()
                if ret:
                    self._lock.acquire()
                    objs = self._currentObjects.copy()
                    self._lock.release()
                    for o in objs:
                        c, s, p1, p2 = o
                        clr = self._getColor(c)
                        ih,iw, _ = img.shape
                        wndrect = cv2.getWindowImageRect(wndname)
                        #cv2.resizeWindow(wndname, iw, ih)
                        #cv2.rectangle(img, (l, t), (r, b), (r,g,b))
                        cv2.rectangle(img, p1, p2, clr, 2)
                        cv2.putText(img, f'c:{c},s:{s}', p1, cv2.FONT_HERSHEY_SIMPLEX, 0.7, clr, 1)
                    cv2.imshow(wndname, img)
                    if cv2.waitKey(1) == 27:
                        break

            cam.release()
            cv2.destroyAllWindows()
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)

        self._stopping = True

if __name__ == '__main__':
    try:
        Program().main(sys.argv[1], sys.argv[2], sys.argv[3])
    except:
        print(f'Use: {sys.argv[0]} video-source-id video-source-uri detection-data-uri')
