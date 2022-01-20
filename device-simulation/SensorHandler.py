from sensors import Sensor
import json
import time
import requests
import threading


class SensorHandler():
    def __init__(self):
        self.deviceType = "sensors"
        # Get mqtt topics from the catalogue-server via a GET request
        # params={"deviceType" : "sensors"})
        r = requests.get('http://172.15.10.20:8080/get/topics')
        devices = r.json()

        self.sensor_topics = devices[self.deviceType]

        # Update json-file
        with open("topics.json", 'r') as file:
            device_topics = json.load(file)
            device_topics[self.deviceType] = self.sensor_topics
        with open("topics.json", 'w') as outfile:
            temp = json.dumps(device_topics, indent=4)
            outfile.write(temp)
        config = json.load(open("config.json"))

        self.sensors = []
        self.broker = config["broker"]
        self.port = config["port"]

        for topic in self.sensor_topics:
            self.sensors += [Sensor(topic, self.broker, self.port)]
        for sensor in self.sensors:
            sensor.start()

    def send(self):
        print("sending")
        for sensor in self.sensors:
            sensor.sendData()

    def updateSensorTopics(self):
        print("updating sensors")
        r = requests.get('http://172.15.10.20:8080/get/topics')
        devices = r.json()
        # Get set difference to find new sensors
        add_topic = list(set(devices["sensors"]) - set(self.sensor_topics))
        # Get set difference to find sensors that need to be removed
        remove_topic = list(set(self.sensor_topics) - set(devices["sensors"]))
        # For each added sensor
        for topic in add_topic:
            # Add the topic to topic list
            self.sensor_topics += [topic]
            # Create new sensor from topic and start it
            new_sensor = Sensor(topic, self.broker, self.port)
            new_sensor.start()
            # Add to list of sensors
            self.sensors += [new_sensor]
            print("Added sensor with topic: " + topic)
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
            self.sensor_topics.remove(topic)
            # List comprehension "trick" to extract sensor object based on sensor.topic
            sensor = [sensor for sensor in self.sensors if sensor.topic == topic][0]
            # Stop the sensor
            sensor.stop()
            # Remove it from list of sensors
            self.sensors.remove(sensor)

            print("Removed sensor with topic: " + topic)
            # Update json-file
            with open("topics.json", 'r') as file:
                topics = json.load(file)
                topics[self.deviceType].remove(topic)
            with open("topics.json", 'w') as outfile:
                temp = json.dumps(topics, indent=4)
                outfile.write(temp)
