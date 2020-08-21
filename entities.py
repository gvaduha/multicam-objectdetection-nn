"""
structures to hold domain objects
"""
# pylint: disable=C0103,R0903

from typing import List
import datetime
import json

class EntityTag:
    """
    Tag class for EntitiesJsonSerializer
    """

class EntitiesJsonSerializer(json.JSONEncoder):
    """
    Serialization for Entity classes (derived from EntityTag)
    but mostly for shitty python datetime support
    """
    def default(self, o):
        if isinstance(o, EntityTag):
            return o.__dict__
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

class CapturedFrame(EntityTag):
    """
    Image with its source and timestamp
    """
    def __init__(self, videostreamid, timestamp, img):
        self.vsid = videostreamid
        self.timestamp = timestamp
        self.img = img

    def __str__(self):
        return f"[{self.vsid}@{self.timestamp}] {self.img}"


class BoundingBox(EntityTag):
    """
    Detected object bounding box
    """
    def __init__(self, left, top, right, bottom):
        self.l = left
        self.t = top
        self.r = right
        self.b = bottom

    def __str__(self):
        return f"({self.t},{self.l}):({self.r},{self.b})"


class DetectedObject(EntityTag):
    """
    Detected object structure (class, probability, bounding box)
    """
    def __init__(self, clazz, probability, bbox: BoundingBox):
        self.c = clazz
        self.p = probability
        self.bbox = bbox

    def __str__(self):
        return f"c:{self.c},p:{self.p},bbox:{self.bbox}"

class DetectedObjectSet(EntityTag):
    """
    List of detected objects with their source and timestamp
    """
    def __init__(self, videostreamid, timestamp, detectedobjs: List[DetectedObject]):
        self.vsid = videostreamid
        self.ts = timestamp
        self.dobjs = detectedobjs

    def __str__(self):
        dobjs = '; '.join(str(x) for x in self.dobjs)
        return f"[{self.vsid}@{self.ts}] [{dobjs}]"


class DetectedObjectsFrame(EntityTag):
    """
    List of all detected objects from all sources for a given timestamp
    """
    def __init__(self, srvid, timestamp, detectedsets: List[DetectedObjectSet]):
        self.srvid = srvid
        self.ts = timestamp
        self.dsets = detectedsets

    def __str__(self):
        dsets = '; '.join(str(x) for x in self.dsets)
        return f"[{self.srvid}@{self.ts}] [{dsets}]"
