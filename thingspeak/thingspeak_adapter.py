import thingspeak
import time
import json
import paho.mqtt.client as PahoMQTT
import json
import requests

class ThingspeakAdaptor():
    def __init__(self, clientID):

        config = json.load(open("config.json"))
        MQTT_config = config['mqtt']
        ts_config = config['thingspeak']

        self.broker = MQTT_config['broker']
        self.port = MQTT_config['port']
        self.ts_channel = thingspeak.Channel(
            id=ts_config['channel_id'], api_key=ts_config['write_key'])
        self.ts_fields = ts_config['field']
    
        # kW used by each light fixture per hour (https://cdn.shopify.com/s/files/1/0135/1827/4660/files/VHA1.pdf?62663)
        self.kWUsedPerActuator = config["kwhPerActuator"]
        # Time stamp for when each actuator was started
        self.actuatorStartedStamp = {}
        # Variable to store energy and cost data in
        self.hours_active_since_update = 0.0
        self.total_energy_costs = 0.0
        self.total_energy_consumption = 0.0
        self.kWUsedPerHour = 0.0
        self.totalTimeActive = 0.0
        
        self.clientID = clientID
        self._isSubscriber = False

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, True)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.start_mqtt()
        self.get_actuator_topics()
        for topic in self.actuator_topics:
            self.actuatorStartedStamp[topic] = None
            self.subscribe(topic)

    def get_actuator_topics(self):
        # Get actuator topics
        r = requests.get('http://172.15.10.20:8080/get/topics')
        devices = r.json()
        self.actuator_topics = devices["actuators"]
        # Update json-file
        with open("topics.json", 'r') as file:
            device_topics = json.load(file)
            device_topics["actuators"] = self.actuator_topics
        with open("topics.json", 'w') as outfile:
            temp = json.dumps(device_topics, indent=4)
            outfile.write(temp)
            
    def ts_update(self, field, data):        
        for key, value in self.ts_fields.items():
            if key == field:
                print(f'Updating field: "{field}" with data: {(data)}')
                # Update thingspeak with measurement
                self.ts_channel.update({value: data})

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def calculateEnergyAndCosts(self):
            r = requests.get('http://172.15.10.40:9090/get/prices')
            energy_prices = r.json()
            price_in_kWh = energy_prices["price_in_kWh"]
            kW_per_hour = len(self.actuator_topics) * self.kWUsedPerActuator
            total_hours_active = self.totalTimeActive / 3600
            self.hours_active_since_update = total_hours_active - self.hours_active_since_update
            energy_consumption = kW_per_hour * self.hours_active_since_update
            self.total_energy_consumption = kW_per_hour * total_hours_active
            self.total_energy_costs += energy_consumption * price_in_kWh
            return self.total_energy_costs, self.total_energy_consumption, price_in_kWh

    def updateActiveTime(self, topic = None):
        """Updates the total active time by looping through each active topic
        and extracting the time"""
        # If no specific topic is requested when calling the method 
        # go through each topic otherwise update only the specific topic
        if topic == None:
            _topics = self.actuator_topics
        else:
            _topics = [topic]
            
        for topic in _topics:
            _time_stamp = self.actuatorStartedStamp[topic]
            if _time_stamp != None:
                # Add the time since it was turned on to the total time active
                self.totalTimeActive += time.time() - _time_stamp
                # Update the time stamp to the current time
                self.actuatorStartedStamp[topic] = time.time()

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        _topic = msg.topic 
        _payload = msg.payload
        d = json.loads(_payload)
        d = d['e'][0]
        status = d['value'] # Assumed to be boolean
        timestamp = float(d['timestamp']) # Assumed to be time stamped with time.time()
        # If the light is turned on
        if status:
            # Add the time since it was turned on to the total time active
            self.totalTimeActive += time.time() - timestamp
            # Update the time stamp to the current time
            self.actuatorStartedStamp[_topic] = time.time()
        # Else, if the light is turned off, set the stamp to None
        else:
            # Extract current active time so no information is lost
            self.updateActiveTime(_topic)
            self.actuatorStartedStamp[_topic] = None

    def subscribe(self, topic):
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        print("subscribed to %s" % (topic))

    def start_mqtt(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

    def stop(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def updateActuatorTopics(self):
        print("updating actuator topics")
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
            self.actuatorStartedStamp[topic] = None
            self.subscribe(topic)
            
            print("Subscribed to topic: " + topic)
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
            self.unsubscribe(topic)
            # Before deleting the time stamp info, update to make sure that no information is lost
            self.updateActiveTime(topic)
            del self.actuatorStartedStamp[topic]
            print("Removed subscription with topic: " + topic)
            # Update json-file
            with open("topics.json", 'r') as file:
                topics = json.load(file)
                topics[self.deviceType].remove(topic)
            with open("topics.json", 'w') as outfile:
                temp = json.dumps(topics, indent=4)
                outfile.write(temp)