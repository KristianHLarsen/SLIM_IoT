import paho.mqtt.client as PahoMQTT
import json

class MessageBroker():
    def __init__(self): 
        self.config = json.load(open('config.json'))
        self.topics = self.config["topics"]
        self.clients = {}
        # for topic in self.topics:            
        #     self.clients[topic] = PahoMQTT.Client(topic, True)
        #     self.clients[topic].on_message = self.on_message
        # print(self.clients)



    #     self.test_client.on_connect = self.on_connect
    #     self.test_client.on_message = self.on_message

    def on_message(self, paho_mqtt , userdata, msg):
        """TODO: read msg.topic and define what to do for each topic"""
        
        pass
    def on_connect (self, paho_mqtt, userdata, flags, rc):
        pass
    def publish(self, topic, msg):
        self.test_client.publish(topic, json.dumps(msg), 2)


if __name__ == "__main__":
    msg_broker = MessageBroker()
    # while True:
    #     pass