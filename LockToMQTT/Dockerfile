ARG BUILD_FROM
FROM $BUILD_FROM
# From python:3.12
RUN \
    apk add --no-cache \
    python3 \
    py3-pip

RUN pip3  install --break-system-packages aiokwikset paho-mqtt coloredlogs
WORKDIR /data
# ADD mqttLock.py /opt/mqttLock.py
COPY mqttLock.py /
COPY run.sh /
RUN chmod a+x /run.sh
# cmd /opt/run.sh
CMD [ "/run.sh" ]
# CMD python3 /opt/mqttLock.py