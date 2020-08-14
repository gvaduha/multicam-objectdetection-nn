import signal
import json
import service as s

service: s.Service = None

def stopHandler(signum, frame):
    print('Stopping...')
    if (service):
        service.stop()

def main():
    with open('config.json') as cfgfile:
        config = json.load(cfgfile)

    print('Press ctrl-c to stop')

    service = s.Service(config)
    service.join()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stopHandler)
    main()
