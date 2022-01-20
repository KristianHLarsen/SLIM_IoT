import random
import json
from MyMQTT import *
import time

# "actuator/3458/factory/34/3"

class DataCollector():
	"""docstring for Sensor"""
	def __init__(self,clientID,broker,baseTopic):
		self.clientID=clientID
		self.baseTopic=baseTopic
		self.client=MyMQTT(clientID,broker,1883, self)
	def run(self):
		self.client.start()
		print('{} has started'.format(self.clientID))
	def end(self):
		self.client.stop()
		print('{} has stopped'.format(self.clientID))
	def follow(self,topic):
		self.client.mySubscribe(topic)
	def notify(self,topic,msg):
		payload=json.loads(msg)
		print(json.dumps(payload,indent=4))

if __name__ == '__main__':
    topic = "actuator/3458/factory/34/3"
    conf = json.load(open("config.json"))
    coll=DataCollector(conf["mqtt"]["user_id"] + "_test",conf["mqtt"]["broker"],"")
    coll.run()
    coll.follow(topic)
    while True:
        pass
