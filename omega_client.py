#!/usr/bin/env python

import time
import socket
import argparse
import logging
import sounddevice as sd


DEVICE = 0
CHANNELS = 1
RATE = 16000
CHUNK = 4096
PORT = 4444
ADDRESS = "localhost"
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
    '-i', '--ipaddress', type=str,
    help='ip server micro')
parser.add_argument(
    '-p', '--port', type=str,
    help='port server micro')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-c', '--channels',
    help='count channels device')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
args = parser.parse_args(remaining)


if args.device:
    DEVICE = args.device
if args.channels:
    CHANNELS = args.channels
if args.ipaddress:
    ADDRESS = args.ipaddress
if args.port:
    PORT = int(args.port)
if args.samplerate:
    RATE = args.samplerate


def callback(in_data, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    clientsocket.send(in_data)


log.info('[+] Start client OMEGA station')
log.info('[INFO] Device information | Device: %s | Channels: %s | Rate: %s' % (DEVICE, CHANNELS, RATE))
log.info('[INFO] Connection information | Address: %s | Port: %s' % (ADDRESS, PORT))

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((ADDRESS, PORT))

rawInputStream = sd.RawInputStream(samplerate=RATE, blocksize=CHUNK, device=DEVICE, dtype='int16', channels=CHANNELS, callback=callback)
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
clientsocket.send(b'quit')
time.sleep(3)
log.debug('[X] Close socket')
clientsocket.close()
