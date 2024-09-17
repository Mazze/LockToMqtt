#!/usr/bin/with-contenv bashio

echo "Hello world!"
python3 /mqttLock.py > /data/run.txt 2>&1 &
python3 -m http.server 8000
