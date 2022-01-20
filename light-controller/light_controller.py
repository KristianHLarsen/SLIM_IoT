# from SensorHandler import SensorHandler
# from ActuatorHandler import ActuatorHandler
import requests
import paho.mqtt.client as mqtt
import threading, time
import json
from MyMQTT import *


class LightController():
    def __init__(self, devices_uri, topics_uri, prices_uri, clientID,broker,port):
        self.__devices_uri = devices_uri
        self.__topics_uri = topics_uri
        self.__prices_uri = prices_uri
        self.clientID=clientID
        self.client=MyMQTT(clientID,broker,port, self)
        self.__short_timer = 10
        self.__long_timer = 15
        self.__threshold = 0.2
        self.__timer = self.__short_timer
        self.__client = mqtt.Client(("Light Controller "+clientID))
        self.__client.connect(broker)
        self.setup()

    
   
    ######## MQTT METHODS #######
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
        # print(json.dumps(payload,indent=4))
        self.analyse_sensor_data(payload)

    ############### LIGHT CONTROL METHODS ##############
    def set_timers(self, short, long, th):
        self.__short_timer = short
        self.__long_timer = long
        self.__threshold = th

    # saves the available sensors in a private var
    def get_sensors(self):
        r = requests.get(self.__devices_uri)
        self.__sensors = r.json()['sensors']
        # print(self.__sensors)

    # saves the available topics in a private var
    def get_topics(self):
        r = requests.get(self.__topics_uri)
        self.__sens_topics = r.json()['sensors']
        self.__act_topics = r.json()['actuators']
    
    def get_prices(self):
        r = requests.get(self.__prices_uri)
        if r.json()['price_in_kWh'] > self.__threshold:
            self.__timer = self.__short_timer
        else:
            self.__timer = self.__long_timer

    # saves the available actuators in a private var
    def get_actuators(self):
        r = requests.get(self.__devices_uri)
        self.__actuators = r.json()['actuators']
        # print(self.__actuators)
    
    # identifies which sensors are located in the same room, and stores their ids and the room in order in two lists
    def same_room_sensors(self):
        self.get_sensors()
        self.__sensors_together = []
        self.__rooms_sens = []
        temp_list = []
        temp_room = []
        for sensor1 in self.__sensors:
            room_sens = []            
            building = sensor1['building']
            floor = sensor1['floor']
            room = sensor1['room']
            for sensor2 in self.__sensors:
                if sensor2['building'] == building and sensor2['floor'] == floor and sensor2['room'] == room:
                    room_sens.append(sensor2['id'])
                    temp_room.append([building, floor, room])
            temp_list.append(room_sens)
        [self.__sensors_together.append(x) for x in temp_list if x not in self.__sensors_together] # remove repetitve entities
        [self.__rooms_sens.append(x) for x in temp_room if x not in self.__rooms_sens] # remove repetitve entities
        # print(str(self.__sensors_together))
        # print(str(self.__rooms_sens))


    # identifies which sensors are located in the same room, and stores their ids and the room in order in two lists
    def same_room_actuators(self):
        self.get_actuators()
        self.__actuators_together = []
        self.__rooms_acts = []
        temp_list = []
        temp_room = []
        for act1 in self.__actuators:
            room_acts = []            
            building = act1['building']
            floor = act1['floor']
            room = act1['room']
            for act2 in self.__actuators:
                if act2['building'] == building and act2['floor'] == floor and act2['room'] == room:
                    room_acts.append(act2['id'])
                    temp_room.append([building, floor, room])
            temp_list.append(room_acts)
        [self.__actuators_together.append(x) for x in temp_list if x not in self.__actuators_together] # remove repetitve entities
        [self.__rooms_acts.append(x) for x in temp_room if x not in self.__rooms_acts] # remove repetitve entities
        # print(str(self.__actuators_together))
        # print(str(self.__rooms_acts))


    # matches which sensors correspond to which actuator based on the room they are in
    # the __pairs variable has the format of [ [ [sensors in room x], [actuators in room x], [building, floor, room x] ], ...   ]
    def sensor_actuator_match(self):
        self.same_room_actuators()
        self.same_room_sensors()
        self.__pairs = [] # containts a list of sensors and actuators in the same room, as well as the room itself
        for i in range(len(self.__rooms_sens)):            
            for j in range(len(self.__rooms_acts)):
                if self.__rooms_sens[i] == self.__rooms_acts[j]:
                    self.__pairs.append({'sensors_together': self.__sensors_together[i], 'actuators_together': self.__actuators_together[j], 'room': self.__rooms_sens[i], 
                    'topics_sensor':[], 'topics_actuator':[], 'sensor_status':False, 'light_status': False, 'timer_timestamp':0})

        # print(str(self.__pairs))

    # checks if the topics for the relevant sensors and actuators exist. Then adds them to "__pairs"
    def setup(self):
        self.get_topics()
        self.sensor_actuator_match()

        for i in range(len(self.__pairs)):
            sens_topic_temp = []
            act_topic_temp = []
            for j in range(len(self.__pairs[i]['sensors_together'])):
                sens_topic_string = "sensor/" + str(self.__pairs[i]['sensors_together'][j]) + "/" + str(self.__pairs[i]['room'][0]) + "/" + str(self.__pairs[i]['room'][1]) + "/" + str(self.__pairs[i]['room'][2])
                # print(sens_topic_string)
                if sens_topic_string in self.__sens_topics:
                    # print("found " + sens_topic_string)
                    sens_topic_temp.append(sens_topic_string)
                else: 
                    print ("ERROR: sensor topic missing: " + sens_topic_string)
                    print ("Please remove the actuator from the registry and add it again (if needed)!")
                    self.__pairs[i]['sensors_together'].pop(j)

            for j in range(len(self.__pairs[i]['actuators_together'])):
                act_topic_string = "actuator/" + str(self.__pairs[i]['actuators_together'][j]) + "/" + str(self.__pairs[i]['room'][0]) + "/" + str(self.__pairs[i]['room'][1]) + "/" + str(self.__pairs[i]['room'][2])
                # print(act_topic_string)
                if act_topic_string in self.__act_topics:
                    # print("found " + act_topic_string)
                    act_topic_temp.append(act_topic_string)
                else: 
                    print ("ERROR: actuator topic missing: " + act_topic_string)
                    print ("Please remove the actuator from the registry and add it again (if needed)!")
                    print (" ")
                    self.__pairs[i]['actuators_together'].pop(j)
            
            if sens_topic_temp and act_topic_temp:
                self.__pairs[i]['topics_sensor'] = sens_topic_temp
                self.__pairs[i]['topics_actuator'] = act_topic_temp
            else:
                print("This room does not have a sensor and/or actuator: " + str(self.__pairs[i][2]))
                self.__pairs.pop(i)

        # print(self.__pairs)
        self.subscribe_to_topics()
        print("Light Controller setup complete!")

        # now the variable self.__pairs has a different format. It includes sensors and 
        # actuators of only controllable and observable rooms, the room address, the sensor topics and actuator topics as follows:
        # [ [ [sensors in room x], [actuators in room x], [building, floor, room x], [sensor topics], [actuator topics], [sensor status], [light status] ], ...   ]
        
    def analyse_sensor_data(self, payload):
        id = payload['bn']
        value = payload['e'][0]['value']
        # print(str(value))

        for i in range(len(self.__pairs)):
            if id in self.__pairs[i]['sensors_together']:
                if value == True:
                    self.__pairs[i]['sensor_status'] = True
                    self.__pairs[i]['light_status'] = True
                    self.__pairs[i]['timer_timestamp'] = time.time()
                    # print("light on!")
                if value == False:
                    if self.__pairs[i]['sensor_status'] == True: # if its 1 then we have just received a 0 for the first time
                        self.__pairs[i]['timer_timestamp'] = time.time()
                        self.__pairs[i]['sensor_status'] = False
                        # print("timer started!")
                        # print(str(time.time()))
    
    def timer_handler(self):
        for i in range(len(self.__pairs)):
            # if light is sensor is out, but light is ON, then we need to check the timer
            if self.__pairs[i]['sensor_status'] == False and self.__pairs[i]['light_status'] == True:
                if time.time() - self.__pairs[i]['timer_timestamp'] > self.__timer:
                    self.__pairs[i]['light_status'] = False
    
    def subscribe_to_topics(self):
        self.run()
        for i in range(len(self.__pairs)):
            for topic in self.__pairs[i]['topics_sensor']:
                self.follow(topic)

    def publish_to_topics(self):
        for i in range(len(self.__pairs)):
            for j in range(len(self.__pairs[i]['topics_actuator'])):
                message = {
                            'buildingID': self.__pairs[i]['room'][0],
                            'floorID': self.__pairs[i]['room'][1],
                            'roomID': self.__pairs[i]['room'][2],
                            'bn': self.__pairs[i]['actuators_together'][j],
                            'e':
                            [
                                {'n': 'light_status', 'value': self.__pairs[i]['light_status'], 'timestamp': str(time.time()), 'unit': 'boolean'},
                            ]
                        }

                self.__client.publish(self.__pairs[i]['topics_actuator'][j], json.dumps(message))
                print("published to: " + self.__pairs[i]['topics_actuator'][j] + " " + str(self.__pairs[i]['light_status']))


    def control_the_lights(self):
        self.get_prices()
        print("timer duration: " + str(self.__timer))
        self.timer_handler()
        for i in range(len(self.__pairs)):
            print("room" + str(i) + ": " + str(self.__pairs[i]['light_status']))
        print("\n")
        self.publish_to_topics()
