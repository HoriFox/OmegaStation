#!/usr/bin/env python

import os
import sys
import logging
import argparse
import socket
import json
import pyaudio
import asyncio
import vosk


FORMAT = pyaudio.paInt16
MODEL = 'model'
LOGLEVEL = logging.DEBUG
LOGFILE = 'station_server.log'


logFormatter = logging.Formatter("[%(asctime)s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log = logging.getLogger()
log.setLevel(LOGLEVEL)
fileHandler = logging.FileHandler(LOGFILE)
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)


parser = argparse.ArgumentParser(description='Assol Station Server', add_help=False)
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
    '-b', '--broadcast', action='store_true', help='broadcast voice')
parser.add_argument(
    '-i', '--ipaddress', type=str, default='',
    help='ipaddress')
parser.add_argument(
    '-p', '--port', type=str, default=4444,
    help='port')
parser.add_argument(
    '-m', '--model', type=str, help='Path to the model')
parser.add_argument(
    '-r', '--samplerate', type=int, default=16000,
    help='Sampling rate')
args = parser.parse_args(remaining)


async def handle_client(reader, writer):
    peername = writer.get_extra_info('peername')
    log.info('[+] Start handle for ip: %s, port: %s' % peername)
    data = None
    while data != b'quit':
         data = await reader.read(CHUNK)
         if rec.AcceptWaveform(data):
             output = rec.Result()
             json_output = json.loads(output)
             final_result = json_output["text"]
             if final_result:
                 log.debug('[F] Final result: %s' % final_result)
         else:
             output = rec.PartialResult()
             json_output = json.loads(output)
             partial_result = json_output["partial"]
             if partial_result:
                 log.debug('[P] Partial result: %s' % partial_result)
         if args.broadcast:
             stream.write(data)
         #response = str(eval(request)) + '\n'
         #writer.write(response.encode('utf8'))
         #await writer.drain()
    writer.close()
    log.info('[-] Stop handle for ip: %s, port: %s' % peername)


async def connect(config):
    log.debug('[*] Server ready to connect clients')
    server = await asyncio.start_server(handle_client, config['address'], config['port'])
    async with server:
        await server.serve_forever()


class OmegaServer:
    def __init__(self):
        pass

    def server_service(self, congif = None):
        if config is None:
            config = {
                'client_device': 0,
                'client_channels': 1,
                'address': args.address,
                'port': args.port,
                'rate': args.samplerate,
                'chunk': 4096,
            }
        if args.broadcast:
            audio = pyaudio.PyAudio()
            stream = audio.open(format=FORMAT, channels=config['client_channels'], rate=config['rate'], 
                                output=True, frames_per_buffer=config['chunk'])

        model = vosk.Model(MODEL)
        rec = vosk.KaldiRecognizer(model, config['rate'])

        try:
            asyncio.run(connect(config))
        except KeyboardInterrupt:
            pass

        log.info('[X] Shutting down')
        if args.broadcast:
            stream.close()
            audio.terminate()


if __name__ == '__main__':
    service = OmegaServer()
    service.server_service()
