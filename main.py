"""
main module
"""
# pylint: disable=C0103,C0301,C0116,W0603,W0613,W0702

import os
import sys
import threading
import time
import signal
import json
import logging
import logging.handlers
import traceback

import service as s

svc: s.Service = None
sigstop = False

def stopProcess():
    global svc
    global sigstop
    print('Stopping...')
    if svc:
        svc.stop()
    sigstop = True

def stopHandler(signum, frame):
    stopProcess()

def unhandledExceptionHandler(exctype, value, tb):
    """
    Python classics: bug from 2005 "fixed" in 2019 adding new handler
    https://bugs.python.org/issue1230540 Pyshit (tm)
    """
    print(exctype)
    print(value)
    traceback.print_tb(tb)
    stopProcess()

def install_thread_excepthook():
    """
    Workaround for sys.excepthook thread bug
    (https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470).
    Call once from __main__ before creating any threads.
    If using psyco, call psycho.cannotcompile(threading.Thread.run)
    since this replaces a new-style class method.
    """
    run_old = threading.Thread.run
    def run(*args, **kwargs):
        try:
            run_old(*args, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            sys.excepthook(*sys.exc_info())
    threading.Thread.run = run


def main():
    global svc
    global sigstop

    sys.excepthook = unhandledExceptionHandler

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(threadName)s %(relativeCreated)6d %(message)s')
    loghdlr = logging.handlers.RotatingFileHandler('multicam-nn-processing.log', maxBytes=1024*1024*50, backupCount=5)
    logger = logging.getLogger('')
    logger.addHandler(loghdlr)
    logger.info('Execution started')

    with open('config.json') as cfgfile:
        config = json.load(cfgfile)

    print('Initializing...')
    svc = s.Service(config, logger)

    signal.signal(signal.SIGINT, stopHandler)
    print('Press ctrl-c to stop')

    while not sigstop:
        time.sleep(1)

    logger.info('Execution finished')


if __name__ == "__main__":
    try:
        install_thread_excepthook()
        main()
    except KeyboardInterrupt:
        print('Aborting!')
        os.abort()
