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
LOGFILE = 'log/station_client.log'


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

    #Tech var
    _config = None
    _is_connected = False
    _error_connection = False

    def __init__(self):
        pass


    def callback(self, in_data, frames, time, status):
        if not self._error_connection:
            """This is called (from a separate thread) for each audio block."""
            sound_density = int(np.linalg.norm(in_data) * 0.0002) * 2 - self.negative_density_bias
            volume = max(self.min_volume, min(sound_density, self.max_volume))
            self.led_service.sound_volume = volume
            try:
                self.clientsocket.send(in_data)
            except BrokenPipeError as bpe:
                log.warning('The server has probably crashed. Error message: %s' % bpe)
                self._error_connection = True


    def connect_server(self):
        config = self._config
        timeout_connection = 4
        if self._is_connected:
            self.clientsocket.close()
            self._is_connected = False
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                log.debug('Try to connect...')
                self.clientsocket.connect((config['address'], config['port']))
            except ConnectionRefusedError as cre:
                log.warning('Server side don`t up. Error message: %s' % cre)
            except Exception as ex:
                log.warning('Unexpected connection error. Error message: %s' % ex)
                exit()
            else:
                log.debug('Successful connection')
                self._is_connected = True
                self._error_connection = False
                break
            if timeout_connection < 60: timeout_connection *= 2
            log.debug('Timeout connection: %s sec' % timeout_connection)
            time.sleep(timeout_connection)


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

        self._config = config

        log.info('[+] Start client OMEGA station')
        log.info('Device information | Device: %s | Channels: %s | Rate: %s' % (config['client_device'], config['client_channels'], config['rate']))
        log.info('Connection information | Address: %s | Port: %s' % (config['address'], config['port']))

        #self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_server()

        self.led_service = LEDAnimation(ColorPro(0, 0, 255))
        self.led_service.run()

        rawInputStream = sd.InputStream(samplerate=config['rate'], blocksize=config['chunk'], device=config['client_device'],
                                       dtype='int16', channels=config['client_channels'], callback=self.callback)
        rawInputStream.start()

        log.info('Press Ctrl+C to stop send microphone stream')
        try:
            self.led_service.state = 'visualization'
            while True:
                if not self._error_connection:
                    responce_all = self.clientsocket.recv(4096).decode('utf8')
                    if responce_all:
                        responce_parts = responce_all.split('\n')
                        responce = responce_parts[0]
                        if len(responce_parts[1]) != 0:
                            log.warning('The package crashed, responce all: %s' % responce_all)
                        log.debug('<<< Responce text: %s' % responce)
                        self.led_service.signal_queue.append(('heil', {'color':ColorPro(0, 255, 0)}))
                else:
                    self.connect_server()
        except KeyboardInterrupt:
            pass
        log.info("[X] Stop client OMEGA station")

        rawInputStream.stop()
        time.sleep(3)
        if not self._error_connection:
            log.debug('[X] Send quit message')
            self.clientsocket.send(b'quit')
            time.sleep(3)
        log.debug('[X] Close socket')
        self.clientsocket.close()
        log.debug('[X] Stop led service')
        self.led_service.stop()

if __name__ == '__main__':
    service = OmegaClient()
    service.client_service()
