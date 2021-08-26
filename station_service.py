import sys
import platform
import json
import argparse


PLATFORM_PROD='Linux-5.10.52+-armv6l-with-debian-10.9'


def load_json(path):
        with open(path, 'r') as f:
                data = json.load(f)
        return data


def load_config(path):
    station_config = {
        'server_address': 'localhost',
        'server_port': 4444,
    }
    load_status = True
    try:
        with open(path) as file:
            data = load_json(path)
            station_config.update(data)
    except Exception as err:
        print('[!] Cant load config from %s: %s' % (path, err))
        print('[!] Load default config')
        load_status = False
    if load_status:
        print('[!] Load config from %s' % path)
    return station_config


parser = argparse.ArgumentParser(description='Omega station launcher')
parser.add_argument('-c', '--config', type=str,
                    default='station.config.json',
                    help='Config file for Omega station')
parser.add_argument('-d', '--debug', action='store_true',
                    help='Debug mode')
args = parser.parse_args()


if __name__ == "__main__":
    print('[LAUNCH] Defining and starting a service')
    service_config = load_config(args.config)
    if platform.platform() == PLATFORM_PROD:
        print('[LAUNCH] Launch client service')
        from client import OmegaClient
        service = OmegaClient()
        service.client_service(service_config)
    else:
        print('[LAUNCH] Launch server service')
        from server import OmegaServer
        service = OmegaServer()
        service.server_service(service_config)
