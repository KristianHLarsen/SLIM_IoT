import random
import json
from MyMQTT import *
import time

class DataCollector():
	"""docstring for Sensor"""
	def __init__(self,clientID,broker,port):
		self.clientID=clientID
		self.client=MyMQTT(clientID,broker,port, self)
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




		
