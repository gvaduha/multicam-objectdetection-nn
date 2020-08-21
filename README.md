# Object detection from multiply video sources

[![License](http://img.shields.io/badge/license-mit-blue.svg?style=flat-square)](https://raw.githubusercontent.com/json-iterator/go/master/LICENSE)
[![Build Status](https://travis-ci.org/gvaduha/multicam-objectdetection-nn.svg?branch=master)](https://travis-ci.org/gvaduha/multicam-objectdetection-nn)

A tiny tool to test and measure different object detection neural networks, capturing set of cameras in the fashion of "process all images at time point".
Tool has pluggable design. Capture done with opencv, classes for NN under test and result processor could be substituted via config.json 

# Pluggable classes
## Neural network class interface
 * def __init__(self, config, logger):
 * def detectObjects(self, img) -> e.DetectedObjectSet:
 * def stop(self):
## Envent result processor
* def __init__(self, config, logger):
* def pushDetectedObjectsFrame(self, frame: e.DetectedObjectsFrame):
* def stop(self):

# Config
[Example](config.js)

Pluggable modules gets config tree under "modules"/"modulename" upon __init__