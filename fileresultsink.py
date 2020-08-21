"""
Implementation of result sink to write json object to file
"""
# pylint: disable=all

import json
import datetime
import os
import entities as e

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
