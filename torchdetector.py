"""
Torch object detector
Disabled:
 error E1101: Module 'torch' has no 'device' member [E:no-member]
"""
# pylint: disable=C0103,C0301,W0703,E1101

from typing import List
import time
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.backbone_utils import resnet_fpn_backbone

import entities as e
from objdetector import ObjectDetector

class TorchDetector:
    """
    Torch object detector
    """
    def __init__(self, config, logger):
        self._logger = logger
        self._threshold = config['threshold']
        modelfile = config['model']
        self._device = config['device'] # cpu, cuda, cuda:0
        backbone = resnet_fpn_backbone('resnet50', False)
        self._model = FasterRCNN(backbone, 8) # 8 classes
        checkpoint = torch.load(modelfile, map_location=self._device)
        self._model.load_state_dict(checkpoint['model_state_dict'])
        device = torch.device(self._device)
        self._model.to(device)
        self._model.eval()


    def stop(self):
        """
        Destruction
        """


    def detectObjects(self, img) -> List[e.DetectedObject]:
        """
        Implementation of detector interface
        """
        _pretransform = A.Compose([A.Resize(800, 1600),
                                   A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
                                   ToTensorV2(),])

        image_tensor = _pretransform(image=img)['image']

        tstart = time.time()

        outputs = self._model.forward(image_tensor.unsqueeze(0).float().to(device=self._device))

        classes = outputs[0]['labels'].detach().cpu().numpy()
        scores = outputs[0]['scores'].detach().cpu().numpy()
        boxes = outputs[0]['boxes'].detach().cpu().numpy()

        self._logger.debug(f'Torch model inferring time: {time.time() - tstart}')

        result = zip(classes, scores, boxes)

        #dobjs: List[e.DetectedObject] = []

        #for c, s, bb in result:
        #    if s < self._threshold:
        #        break
        #    dobjs.append(e.DetectedObject(int(c), float(s),
        #                                  e.BoundingBox(int(bb[0]*height), int(bb[1]*width), int(bb[2]*height), int(bb[3]*width))))

        #return dobjs
        height = img.shape[0]
        width = img.shape[1]

        return ObjectDetector.getDetectedObjectsCollection(result, height, width, self._threshold)
