from typing import List

class CapturedFrame:
    def __init__(self, id, timestamp, img):
        self.id = id
        self.timestamp = timestamp
        self.img = img

class BoundingBox:
    def __init__(self, left, top, right, bottom):
        self.l = left
        self.t = top
        self.r = right
        self.b = bottom

class DetectedObject:
    def __init__(self, probability, bbox: BoundingBox):
        self.p = probability
        self.bbox = bbox

class DetectedObjectSet:
    def __init__(self, videostreamid, timestamp, detectedobjs: List[DetectedObject]):
        self.vsid = videostreamid
        self.ts = timestamp
        self.dobjs = detectedobjs

class DetectedObjectsFrame:
    def __init__(self, srvid, timestamp, detectedsets: DetectedObjectSet):
        self.srvid = srvid
        self.ts = timestamp
        self.dsets = detectedsets
