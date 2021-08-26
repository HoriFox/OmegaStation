#!/usr/bin/env python

import time
import socket
import argparse
import logging
import sounddevice as sd
import numpy as np
from rpi_ws281x import *
from led_tools import LEDAnimation, ColorPro

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

    min_volume = 0
    max_volume = 100
    negative_density_bias = 6

    def __init__(self):
        pass

    def callback(self, in_data, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        sound_density = int(np.linalg.norm(in_data) * 0.0002) * 2 - self.negative_density_bias
        volume = max(self.min_volume, min(sound_density, self.max_volume))
        self.led_service.sound_volume = volume
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

        self.led_service = LEDAnimation(ColorPro(0, 0, 255))
        self.led_service.run()

        rawInputStream = sd.InputStream(samplerate=config['rate'], blocksize=config['chunk'], device=config['client_device'],
                                       dtype='int16', channels=config['client_channels'], callback=self.callback)
        rawInputStream.start()

        log.debug('[INFO] Press Ctrl+C to stop send microphone stream')
        try:
            self.led_service.state = 'visualization'
            while True:
                responce_all = self.clientsocket.recv(4096).decode('utf8')
                responce_parts = responce_all.split('\n')
                responce = responce_parts[0]
                if len(responce_parts[1]) != 0:
                    log.warning('The package crashed, responce all: %s' % responce_all)
                self.led_service.signal_queue.append(('heil', {'color':ColorPro(0, 255, 0)}))
                #self.led_service.state = 'loading'
                #time.sleep(2)
                #self.led_service.signal_queue.append('heil')
                #time.sleep(2)
                #self.led_service.state = 'visualization'
                #time.sleep(10)
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
