#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "You must be root to do this." 1>&2
   exit 1
fi

echo "Create log files..."
mkdir /var/log/omegastation
touch /var/log/omegastation/station_client.log
touch /var/log/omegastation/station_server.log
chmod -R 777 /var/log/omegastation/

echo "Set systemd file to systemd dir..."
cp systemdfile/omegastation.service /etc/systemd/system/omegastation.service

echo "Reload systemd daemon..."
systemctl daemon-reload

echo "Status check..."
systemctl status omegastation.service
