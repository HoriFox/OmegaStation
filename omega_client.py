#!/usr/bin/env python

import time
import socket
import argparse
import logging
import sounddevice as sd


LOGLEVEL = logging.DEBUG
LOGFILE = 'station_client.log'


logFormatter = logging.Formatter("[%(asctime)s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log = logging.getLogger()
log.setLevel(LOGLEVEL)
fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-a', '--address', type=str, default="localhost",
    help='ip server')
parser.add_argument(
    '-p', '--port', type=str, default=4444,
    help='port server')
parser.add_argument(
    '-d', '--device', type=int_or_str, default=0,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-c', '--channels', default=1,
    help='count channels device')
parser.add_argument(
    '-r', '--samplerate', type=int, default=16000,
    help='sampling rate')
args = parser.parse_args(remaining)


class OmegaClient:
    def __init__(self):
        pass

    def callback(self, in_data, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        self.clientsocket.send(in_data)


    def client_service(self, config = None):
        if config is None:
            config = {
                'client_device': args.device,
                'client_channels': args.channels,
                'address': args.address,
                'port': args.port,
                'rate': args.samplerate,
                'chunk': 4096,
            }

        log.info('[+] Start client OMEGA station')
        log.info('[INFO] Device information | Device: %s | Channels: %s | Rate: %s' % (config['client_device'], config['client_channels'], config['rate']))
        log.info('[INFO] Connection information | Address: %s | Port: %s' % (config['address'], config['port']))

        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((config['address'], config['port']))

        rawInputStream = sd.RawInputStream(samplerate=config['rate'], blocksize=config['chunk'], device=config['client_device'],
                                       dtype='int16', channels=config['client_channels'], callback=self.callback)
        rawInputStream.start()

        log.debug('[INFO] Press Ctrl+C to stop send microphone stream')
        try:
            while True:
                pass
        except KeyboardInterrupt:
            pass
        log.info("[X] Stop client OMEGA station")

        rawInputStream.stop()
        time.sleep(3)
        log.debug('[X] Send quit message')
        self.clientsocket.send(b'quit')
        time.sleep(3)
        log.debug('[X] Close socket')
        self.clientsocket.close()


if __name__ == '__main__':
    service = OmegaClient()
    service.client_service()
