#!/usr/bin/env python

import os
import sys
import logging
import argparse
import socket
import json
#import pyaudio
import asyncio
import vosk
import krionard_request


#FORMAT = pyaudio.paInt16
MODEL = 'model'
LOGLEVEL = logging.DEBUG
LOGFILE = 'station_server.log'
ACTIVATIONWORD = 'омега'
#ACTIVATIONWORD = ''

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


class OmegaServer:
    config = None


    def __init__(self):
        pass

    async def handle_client(self, reader, writer):
        peername = writer.get_extra_info('peername')
        log.info('[+] Start handle for ip: %s, port: %s' % peername)
        data = None
        while data != b'quit':
             data = await reader.read(self.config['chunk'])
             if self.rec.AcceptWaveform(data):
                 output = self.rec.Result()
                 json_output = json.loads(output)
                 final_result = json_output["text"]
                 if final_result:
                     log.debug('[F] Final result: %s' % final_result)
                     aword_position = final_result.rfind(ACTIVATIONWORD)
                     if aword_position != -1:
                         # Take the last array of the command [omega command item OMEGA COMMAND ITEM] - take that capslock
                         tokens_without_activation = final_result[aword_position + len(ACTIVATIONWORD) + 1:].split()
                         print('tokens_without_activation', tokens_without_activation)
                         response = krionard_request.request_krionard(tokens_without_activation)
                         print('Send text response to client: "%s"' % response.split('\n')[0])
                         writer.write(response.encode('utf8'))
                         await writer.drain()
                     else:
                         log.debug('[X] Request not sent, missing activation word!')
             else:
                 output = self.rec.PartialResult()
                 json_output = json.loads(output)
                 partial_result = json_output["partial"]
                 if partial_result:
                     log.debug('[P] Partial result: %s' % partial_result)
             #if args.broadcast:
             #    stream.write(data)
             #response = str(eval(request)) + '\n'
             #writer.write(response.encode('utf8'))
             #await writer.drain()
        writer.close()
        log.info('[-] Stop handle for ip: %s, port: %s' % peername)


    async def connect(self):
        log.debug('[*] Server ready to connect clients')
        server = await asyncio.start_server(self.handle_client, self.config['address'], self.config['port'])
        async with server:
            await server.serve_forever()


    def server_service(self, config = None):
        if config is None:
            config = {
                'client_device': 0,
                'client_channels': 1,
                'address': args.address,
                'port': args.port,
                'rate': args.samplerate,
                'chunk': 4096,
            }
        self.config = config

        #if args.broadcast:
            #audio = pyaudio.PyAudio()
            #stream = audio.open(format=FORMAT, channels=self.config['client_channels'], rate=self.config['rate'], 
            #                    output=True, frames_per_buffer=self.config['chunk'])

        model = vosk.Model(MODEL)
        self.rec = vosk.KaldiRecognizer(model, self.config['rate'])

        try:
            asyncio.run(self.connect())
        except KeyboardInterrupt:
            pass

        log.info('[X] Shutting down')
        #if args.broadcast:
            #stream.close()
            #audio.terminate()


if __name__ == '__main__':
    service = OmegaServer(None)
    service.server_service()
