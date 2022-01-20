from MyMQTT import MyMQTT
import time
import json


class LightActuator:
    def __init__(self, topic, broker, port):
        self.topic = topic
        actuator_info = topic.split("/")
        self.id = actuator_info[1]
        self.building = actuator_info[2]
        self.floor = actuator_info[3]
        self.room = actuator_info[4]

        self.client = MyMQTT(self.id, broker, port, notifier = self)

        self.status = None

    def start(self):
        self.client.start()
        self.client.mySubscribe(self.topic)

    def stop(self):
        self.client.stop()

    def notify(self, topic, msg):
        d = json.loads(msg)
        d = d['e'][0]
        self.status = d['value']
        timestamp = d['timestamp']
        print(
            f'The led has been set to {self.status} at time {timestamp}')
