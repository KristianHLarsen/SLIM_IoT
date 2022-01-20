import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import json

mqttBroker = "test.mosquitto.org"
client = mqtt.Client("Temperature_Inside")
client.connect(mqttBroker)
baseTopic = "sensor/124/factory/34/3"
floor = 4

message = {
            'buildingID': "factory",
            'floorID': "34",
            'roomID': "3",
            'bn': "124",
            'e':
            [
                {'n': 'motion', 'value': False, 'timestamp': '', 'unit': 'boolean'},
            ]
        }

while True:
    randNumber = uniform(20.0, 21.0)
    client.publish(baseTopic, json.dumps(message))
    client.publish(baseTopic + "/" + str(floor) + "/2", floor)
    print("Just published " + json.dumps(message) + " to Topic " + baseTopic)
    time.sleep(1)
