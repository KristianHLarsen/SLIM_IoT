import random
import json
from MyMQTT import *
import time
import requests

# "actuator/3458/factory/34/3"

class DataCollector():
	"""docstring for Sensor"""
	def __init__(self,clientID,broker,baseTopic):
		self.clientID=clientID
		self.baseTopic=baseTopic
		self.client=MyMQTT(clientID,broker,1883, self)
		self.value = None
		self.id = 0
	def run(self):
		self.client.start()
		# print('{} has started'.format(self.clientID))
	def end(self):
		self.client.stop()
		# print('{} has stopped'.format(self.clientID))
	def follow(self,topic):
		self.client.mySubscribe(topic)
	def notify(self,topic,msg):
		self.msg=json.loads(msg)
		# print(json.dumps(self.msg,indent=4))
		self.id = self.msg['bn']
		self.value = self.msg['e'][0]['value']
	def get_value_and_id(self):
		return [self.value, self.id]


if __name__ == '__main__':
	r = requests.get("http://0.0.0.0:8080/get/topics")
	sens_topics = r.json()['sensors']
	act_topics = r.json()['actuators']
	# print(str(act_topics))

	actuators = []
	sensors = []

	conf = json.load(open("config.json"))

	for i in range(len(act_topics)):
		new_actuator = DataCollector(conf["mqtt"]["user_id"] + str(i) + "act",conf["mqtt"]["broker"],"")
		actuators += [new_actuator]
		actuators[i].run()
		actuators[i].follow(act_topics[i])
		# print(str(act_topics[i]))

	for i in range(len(sens_topics)):
		new_sensor = DataCollector(conf["mqtt"]["user_id"] + str(i) + "sens",conf["mqtt"]["broker"],"")
		sensors += [new_sensor]
		sensors[i].run()
		sensors[i].follow(sens_topics[i])
		# print(str(sens_topics[i]))		

	while True:
		time.sleep(1)
		print("-------------- ACTUATORS ------------------")
		print("-------ID--------------------STATUS--------")
		for actuator in actuators:
			print("------" + str(actuator.get_value_and_id()[1]) + "------------------" + str(actuator.get_value_and_id()[0]) + "-----")
			
		("------------------------------------------------")
		print("--------------- SENSORS -------------------")
		print("-------ID--------------------STATUS--------")
		for sensor in sensors:
			print("------" + str(sensor.get_value_and_id()[1]) + "------------------" + str(sensor.get_value_and_id()[0]) + "-----")
			
	


