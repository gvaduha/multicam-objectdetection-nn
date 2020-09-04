"""
Tensorflow object detector
"""
# pylint: disable=C0103,C0301,R0902

import time
from typing import List
import tensorflow as tf

import entities as e
from objdetector import ObjectDetector

class TensorFlowDetector:
    """
    Tensor flow object detector
    """
    def __init__(self, config, logger):
        self._logger = logger
        self._threshold = config['threshold']
        modelfile = config['model']
        with tf.io.gfile.GFile(modelfile, 'rb') as f:
            graph = tf.compat.v1.GraphDef()
            graph.ParseFromString(f.read())

        self._logger.debug('TF model placeholders:')
        phnodes = [n.name + ' => ' +  n.op for n in graph.node if n.op in 'Placeholder']
        for node in phnodes:
            self._logger.debug(node)
        self._logger.debug('TF model placeholders end.')

        with tf.compat.v1.Graph().as_default() as defgraph:
            #name='' is *absolutely* required, or you've got lots of weird errors (pyece of shithon)
            tf.compat.v1.import_graph_def(graph, name='')

        self._session = tf.compat.v1.Session(graph=defgraph)

        self._image_tensor = defgraph.get_tensor_by_name('image_tensor:0')
        self._boxes = defgraph.get_tensor_by_name('detection_boxes:0')
        self._scores = defgraph.get_tensor_by_name('detection_scores:0')
        self._classes = defgraph.get_tensor_by_name('detection_classes:0')
        self._num_detections = defgraph.get_tensor_by_name('num_detections:0')


    def stop(self):
        """
        Destruction
        """
        self._session.close()


    def detectObjects(self, img) -> List[e.DetectedObject]:
        """
        Implementation of detector interface
        """
        h, w, _ = img.shape
        img = img[:, :, [2, 1, 0]]  # BGR2RGB

        tstart = time.time()

        (boxes, scores, classes, _) = self._session.run(
            [self._boxes, self._scores, self._classes, self._num_detections],
            feed_dict={self._image_tensor: img.reshape(1, h, w, 3)})

        self._logger.debug(f'TF model inferring time: {time.time() - tstart}')

        result = zip(classes[0], scores[0], boxes[0])

        return ObjectDetector.getDetectedObjectsCollection(result, h, w, self._threshold)
