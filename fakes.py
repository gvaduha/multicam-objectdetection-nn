"""
fake implementations
"""
# pylint: disable=all

import entities as e

class FakeNn():
    def __init__(self, config, logger):
        self._logger = logger

    def detectObjects(self, img) -> e.DetectedObjectSet:
        dobjs = [e.DetectedObject(1, 0.8, e.BoundingBox(10, 10, 20, 30)), e.DetectedObject(2, 0.5, e.BoundingBox(55, 35, 88, 55))]
        return dobjs

    def stop(self):
        pass

