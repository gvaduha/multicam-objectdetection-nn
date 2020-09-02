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

# Config
[Full example](config.json)

## Main
```
  "runintervalsec": 1.0
```

## Modules config
Pluggable modules gets config tree under "modules"/"modulename" upon __init__

  ```
  "modules": {
    "WriteJsonResultSink": {
      "file": "./results.log"
    },
    "FlaskResultSink": {
      "server": "0.0.0.0:5555",
      "resultep": "/currentresult"
    },
    "TensorFlowDetector": {
      "model": "models/tf.model",
      "threshold": 0.1
    },
    "TorchDetector": {
      "model": "models/torch.model",
      "threshold": 0.1,
      "device": "cpu"
    }
  },
  ```
  
  ## Cams config
  ```
  "cams": [
    {
      "vsid": 1,
      "uri": "rtsp://admin:admin@cam1/h264"
    },
    {
      "vsid": 2,
      "uri": "rtsp://admin:admin@cam2"
    }
  ]
  ```
