# Object detection from multiply video sources

[![License](http://img.shields.io/badge/license-mit-blue.svg?style=flat-square)](https://raw.githubusercontent.com/json-iterator/go/master/LICENSE)
[![Build Status](https://travis-ci.org/gvaduha/multicam-objectdetection-nn.svg?branch=master)](https://travis-ci.org/gvaduha/multicam-objectdetection-nn)

Online multicam object detection mini framework. Currently doesn't have an object tracker and supposed it is an external component aggregating detection results from group of detection servers. Started as a tool to test and measure different object detection neural networks, capturing set of cameras in the fashion of "process all images at time point".
Tool has pluggable design. Capture done with opencv, classes for NN under test and result processor could be substituted via config.json 

# Pluggable classes
## Neural network class interface
* def __init__(self, config, logger):
* def detectObjects(self, img) -> List[e.DetectedObject]:
* def stop(self):

Available implementations:
* fakes::FakeNn
```
  "nn": {
    "module": "fakes",
    "class": "FakeNn"
  },
```

* tfdetector::TensorFlowDetector
```
  "nn": {
    "module": "tfdetector",
    "class": "TensorFlowDetector"
  },
```

* torchdetector::TorchDetector
```
  "nn": {
    "module": "torchdetector",
    "class": "TorchDetector"
  },
```

## Envent result processor
* def __init__(self, config, logger):
* def pushDetectedObjectsFrame(self, frame: e.DetectedObjectsFrame):
* def stop(self):

Available implementations:
* fileresultsink::WriteJsonResultSink
```
  "resultsink": {
    "module": "fileresultsink",
    "class": "WriteJsonResultSink"
  },
```

* webservice::FlaskResultSink
```
  "resultsink": {
    "module": "webservice",
    "class": "FlaskResultSink"
  },
```

  serving results @ /currentresult

# Config
[Example](config.json)

Pluggable modules gets config tree under "modules"/"modulename" upon __init__
