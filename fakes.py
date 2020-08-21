"""
fake implementations
"""
# pylint: disable=all

import json
import datetime
import os
import entities as e

class FakeNn():
    def __init__(self, config, logger):
        self._logger = logger

    def detectObjects(self, img) -> e.DetectedObjectSet:
        dobjs = [e.DetectedObject(1, 0.8, e.BoundingBox(10, 10, 20, 30)), e.DetectedObject(2, 0.5, e.BoundingBox(55, 35, 88, 55))]
        return dobjs

    def stop(self):
        pass

class WriteJsonResultSink():
    def __init__(self, config, logger):
        self._stopping = False
        self._resfile = open(config['file'], 'a+')
        self._logger = logger

    def pushDetectedObjectsFrame(self, frame: e.DetectedObjectsFrame):
        self._logger.debug(frame)
        jsonobj = json.dumps(frame, cls=e.EntitiesJsonSerializer)
        self._resfile.write(f'{jsonobj}{os.linesep}')

    def stop(self):
        self._resfile.close()
