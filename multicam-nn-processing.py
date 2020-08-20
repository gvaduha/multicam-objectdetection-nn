"""
main module
"""
# pylint: disable=C0103,C0301,C0116,W0603,W0613

import os
import time
import signal
import json
import logging
import logging.handlers

import service as s

svc: s.Service = None
sigstop = False

def stopHandler(signum, frame):
    global svc
    global sigstop
    print('Stopping...')
    if svc:
        svc.stop()
    sigstop = True

def main():
    global svc
    global sigstop

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(threadName)s %(relativeCreated)6d %(message)s')
    loghdlr = logging.handlers.RotatingFileHandler('multicam-nn-processing.log', maxBytes=1024*1024*50, backupCount=5)
    logger = logging.getLogger('')
    logger.addHandler(loghdlr)
    logger.debug('Execution started')

    with open('config.json') as cfgfile:
        config = json.load(cfgfile)

    print('Initializing...')
    svc = s.Service(config, logger)

    signal.signal(signal.SIGINT, stopHandler)
    print('Press ctrl-c to stop')

    while not sigstop:
        time.sleep(1)

    logger.debug('Execution finished')


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Aborting!')
        os.abort()
