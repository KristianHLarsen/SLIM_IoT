from actuator import LightActuator
import json
import time
import requests
import threading


class ActuatorHandler():
    def __init__(self):
        self.deviceType = "actuators"
        # Get mqtt topics from the catalogue-server via a GET request
        # params = {"deviceType": "sensors"})
        r = requests.get('http://172.15.10.20:8080/get/topics')
        devices = r.json()
        self.actuator_topics = devices[self.deviceType]

        # Update json-file
        with open("topics.json", 'r') as file:
            device_topics = json.load(file)
            device_topics[self.deviceType] = self.actuator_topics
        with open("topics.json", 'w') as outfile:
            temp = json.dumps(device_topics, indent=4)
            outfile.write(temp)

        config = json.load(open("config.json"))
        self.actuators = []

        self.broker = config["broker"]
        self.port = config["port"]

        for topic in self.actuator_topics:
            self.actuators += [LightActuator(topic, self.broker, self.port)]

        for actuator in self.actuators:
            actuator.start()

    def updateActuatorTopics(self):
        print("updating actuators")
        r = requests.get('http://172.15.10.20:8080/get/topics')
        devices = r.json()
        # Get set difference to find new sensors
        add_topic = list(set(devices[self.deviceType]) - set(self.actuator_topics))
        # Get set difference to find sensors that need to be removed
        remove_topic = list(set(self.actuator_topics) - set(devices[self.deviceType]))
        # For each added sensor
        for topic in add_topic:
            # Add the topic to topic list
            self.actuator_topics += [topic]
            # Create new sensor from topic and start it
            new_actuator = LightActuator(topic, self.broker, self.port)
            new_actuator.start()
            # Add to list of sensors
            self.actuators += [new_actuator]
            print("Added actuator with topic: " + topic)

            # Update json-file
            with open("topics.json", 'r') as file:
                topics = json.load(file)
                topics[self.deviceType].append(topic)
            with open("topics.json", 'w') as outfile:
                temp = json.dumps(topics, indent=4)
                outfile.write(temp)

        # Remove sensor topics
        for topic in remove_topic:
            # Remove the topic from topic list
            self.actuator_topics.remove(topic)
            # List comprehension "trick" to extract sensor object based on sensor.topic
            actuator = [actuator for actuator in self.actuators if actuator.topic == topic][0]
            # Stop the sensor
            actuator.stop()
            # Remove it from list of sensors
            self.actuators.remove(actuator)

            print("Removed actuator with topic: " + topic)
            # Update json-file
            with open("topics.json", 'r') as file:
                topics = json.load(file)
                topics[self.deviceType].remove(topic)
            with open("topics.json", 'w') as outfile:
                temp = json.dumps(topics, indent=4)
                outfile.write(temp)
