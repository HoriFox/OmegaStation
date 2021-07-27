import sys
import argparse
import logging

logfile = 'station.log'
logFormatter = logging.Formatter("[%(asctime)s] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
log = logging.getLogger()
log.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(logfile)
fileHandler.setFormatter(logFormatter)
log.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)

parser = argparse.ArgumentParser(description='Assol Station')
parser.add_argument('-c', '--config', type=str,
                    default='/etc/assol/station.config.json',
                    help='Config file for Assol station')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Debug mode')
args = parser.parse_args()

if __name__ == "__main__":
    log.info('Hello world!')
