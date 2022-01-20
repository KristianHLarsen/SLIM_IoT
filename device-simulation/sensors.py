import random
import json
from MyMQTT import MyMQTT
import time
# from simplePublisher import MyPublisher


class Sensor:
    """docstring for Sensor"""
    def __init__(self, topic, broker, port):
        self.topic = topic
        sensor_info = topic.split("/")
        self.id = sensor_info[1]
        self.building = sensor_info[2]
        self.floor = sensor_info[3]
        self.room = sensor_info[4]
        # Randomly set the behaviour of the simulated data
        # 0 = no movement, 1 = infrequent movement
        # 2 = frequent movement, 3 = always movement
        self.behaviour = 2 #random.randint(0, 3)
        
        self.client = MyMQTT(self.id, broker, port, None)
        self.__message = {
            'buildingID': self.building,
            'floorID': self.floor,
            'roomID': self.room,
            'bn': self.id,
            'e':
            [
                {'n': 'motion', 'value': '', 'timestamp': '', 'unit': 'boolean'},
            ]
        }

    def sendData(self):
        message = self.__message

        # If random number is greater than the threshold = movement detected
        if self.behaviour == 0:
            message['e'][0]['value'] = False

        if self.behaviour == 1: # 1% chance for movement to be detected
            if random.randint(0, 100) > 99:
                message['e'][0]['value'] = True
            else:
                message['e'][0]['value'] = False

        if self.behaviour == 2: # 30% chance to detect movement
            if random.randint(0, 10) > 7:
                message['e'][0]['value'] = True
            else:
                message['e'][0]['value'] = False

        if self.behaviour == 3:            
            message['e'][0]['value'] = True

        message['e'][0]['timestamp'] = str(time.time())
        self.client.myPublish(self.topic, message)

    def start(self):
        self.client.start()

    def stop(self):
        self.client.stop()