import entities as e

class FakeNn():
    def detectObjects(self, frame: e.CapturedFrame) -> e.DetectedObjectSet :
        dobjs = [e.DetectedObject(1, 0.8, e.BoundingBox(10, 10, 20, 30)), e.DetectedObject(2, 0.5, e.BoundingBox(55, 35, 88, 55))]
        return e.DetectedObjectSet(frame.vsid, frame.timestamp, dobjs)
