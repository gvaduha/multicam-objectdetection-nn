import entities as e

class FakeNn():
    def detectObjects(self, frame: e.CapturedFrame) -> e.DetectedObjectSet :
        return 42
