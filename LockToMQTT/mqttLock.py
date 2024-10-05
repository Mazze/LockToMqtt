# python 3.11
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
# from paho.mqtt import client as mqtt_client
import random
import time
import asyncio
import datetime
from aiokwikset import API
import json
import threading
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
logger.info("this is an informational message")
logger.warning("this is a warning message")
logger.error("this is an error message")

with open('options.json', 'r') as file:
    haOptions = json.load(file)

MessageEvent =threading.Event()



async def lockDev(method,client,userdata):
    device_info = await userdata['api'].device.get_device_info(userdata['devices'][0]['deviceid'])
    if method == "UNLOCK":
        client.publish("door/state",json.dumps({"doorstatus":"UNLOCKING"}),retain=True)
        await userdata['api'].device.unlock_device(device_info, userdata['user_info'])

    else:
        client.publish("door/state",json.dumps({"doorstatus":"LOCKING"}),retain=True)
        await userdata['api'].device.lock_device(device_info, userdata['user_info'])

async def main() -> None:

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, reason_code ,a):
        print(f"Connected with result code {reason_code}")
        print(F"Start")
        f = open("demofile2.txt", "a")
        f.write("Connected with MQTT\n")
        f.close()
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("$SYS/#")
    def on_message(client, userdata, message):
        if message.topic =="door/set":
            try:
                asJson =message.payload.decode('utf8')
                data=json.loads(asJson)
                print(str(data['action']))
                if data['action'] == "UNLOCK":
                    MessageEvent.set()

                asyncio.run(lockDev(data['action'],client,userdata))
                time.sleep(1)

            except Exception as error    :
                print("Error on topic door/set  ",error)
                f = open("demofile2.txt", "a")
                f.write("Error on topic door/set  ")
                f.write(error)
                f.write("\n")
                f.close()
            print("Done")


    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        print("Mid:{}".format(mid))
        print("reason_code_list:{}".format(reason_code_list))
    def on_log(client, userdata, paho_log_level, messages):
        if paho_log_level == mqtt.LogLevel.MQTT_LOG_ERR:
            print(messages)
    print(F"Start")
    f = open("demofile2.txt", "a")
    f.write("Start\n")
    f.close()
    try:
        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.on_log = on_log
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.on_subscribe = on_subscribe
        mqttc.username_pw_set(haOptions["broker_username"], haOptions["broker_password"])



        f = open("demofile2.txt", "a")
        f.write("Connected to lock")
        f.close()

        api = API(haOptions["username"])
        api.username = haOptions['username']
        api.user_pool_region = haOptions['user_pool_region']
        api.id_token = haOptions['id_token']
        api.access_token = haOptions['access_token']
        api.refresh_token = haOptions['refresh_token']
        api.user_pool_id = haOptions['user_pool_id']
        api.client_id = haOptions['client_id']
        a = await api.renew_access_token()
        user_info = await api.user.get_info()

        homes = await api.user.get_homes()
        devices = await api.device.get_devices(homes[0]['homeid'])
        device_info = await api.device.get_device_info(devices[0]['deviceid'])
        f = open("demofile2.txt", "a")
        # f.write(a)
        f.write(str(user_info)+"\n")
        f.write(str(homes)+"\n")
        f.write(str(devices)+"\n")
        f.write(str(device_info)+"\n")
        f.close()
        ud= {}
        ud['api'] = api
        ud['device_info']=device_info
        ud['devices'] = devices
        ud['user_info'] = await api.user.get_info()

        print(F"Connecting")
        f = open("demofile2.txt", "a")
        f.write("Connection\n")
        f.close()
        mqttc.connect(haOptions["broker"], haOptions["broker_port"], 60)
        mqttc.loop_start()
        mqttc.subscribe("door/set")
        mqttc.user_data_set(ud)
        # mqttc.on_message = on_subscribtion
        while True:
            device_info = await api.device.get_device_info(devices[0]['deviceid'])
            print(F"Pubish")
            f = open("demofile2.txt", "a")
            f.write("publish\n")
            f.write(str(device_info))
            f.close()
            attributeJson= {
                "batterystatus":device_info['batterystatus'],
                "batterypercentage":device_info['batterypercentage'],
                "lastLockStatusTime":datetime.datetime.fromtimestamp(device_info['lastLockStatusTime']).strftime("%m/%d/%Y, %H:%M:%S")
            }
            mqttc.publish("door/state",json.dumps({"doorstatus":device_info['doorstatus']}),retain=True)
            mqttc.publish("door/attributes", json.dumps(attributeJson),retain=True)
            # mqttc.publish("door/batterystatus", device_info['batterystatus'],retain=True)
            # mqttc.publish("door/batterypercentage", device_info['batterypercentage'],retain=True)
            # mqttc.publish("door/doorstatus", device_info['doorstatus'],retain=True)
            # mqttc.publish("door/lastLockStatusTime", device_info['lastLockStatusTime'],retain=True)
            if MessageEvent.wait(60.0):
                print("Send different")
                mqttc.publish("door/state",json.dumps({"doorstatus":"UNLOCKING"}),retain=True)
                MessageEvent.clear()
                time.sleep(10)
        print(F"Stop")
        mqttc.loop_stop()
    except Exception as err:
        f = open("demofile2.txt", "a")
        f.write(f"\n\nUnexpected {err=}, {type(err)=}\n")
        f.close()
        print(f"Unexpected {err=}, {type(err)=}")
        raise


f = open("demofile2.txt", "w")
f.write("\nstart")
f.close()
asyncio.run(main())
