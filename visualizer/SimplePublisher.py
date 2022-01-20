import paho.mqtt.client as mqtt
from random import randrange, uniform
import time
import json
import requests

mqttBroker = "test.mosquitto.org"
client = mqtt.Client("Temperature_Inside")
client.connect(mqttBroker)
baseTopic = 'actuator/3456/factory/34/1'
floor = 4


r = requests.get("http://172.15.10.20:8080/get/topics")
sens_topics = r.json()['sensors']
act_topics = r.json()['actuators']

message_sens = {
            'buildingID': "factory",
            'floorID': "34",
            'roomID': "1",
            'bn': "sens1",
            'e':
            [
                {'n': 'motion', 'value': False, 'timestamp': '', 'unit': 'boolean'},
            ]
        }

message_act = {
            'buildingID': "factory",
            'floorID': "34",
            'roomID': "1",
            'bn': "act1",
            'e':
            [
                {'n': 'motion', 'value': False, 'timestamp': '', 'unit': 'boolean'},
            ]
        }

while True:
    # randNumber = uniform(20.0, 21.0)
    for topic in sens_topics:
        client.publish(topic, json.dumps(message_sens))
        print("Just published " + json.dumps(message_sens) + " to Topic " + topic)
    for topic in act_topics:
        client.publish(topic, json.dumps(message_act))
        print("Just published " + json.dumps(message_act) + " to Topic " + topic)
    time.sleep(1)
