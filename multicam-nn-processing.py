import signal
import json
import service as s

svc: s.Service = None

def stopHandler(signum, frame):
    global svc
    print('Stopping...')
    if (svc):
        svc.stop()

def main():
    global svc
    with open('config.json') as cfgfile:
        config = json.load(cfgfile)

    print('Initializing...')
    svc = s.Service(config)
    print('Press ctrl-c to stop')
    svc.join()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stopHandler)
    main()
