# from SensorHandler import SensorHandler
# from ActuatorHandler import ActuatorHandler
import requests
import threading, time
import json
from light_controller import *
# from DataCollector import DataCollector

def get_device_url():
    with open("config.json", 'r') as file:
        json_object = json.load(file)
        rest = json_object['rest']
        return rest['host'] + ":" + rest['port'] + rest['getdevices']

def get_topic_url():
    with open("config.json", 'r') as file:
        json_object = json.load(file)
        rest = json_object['rest']
        return rest['host'] + ":" + rest['port'] + rest['gettopics']

def get_price_url():
    with open("config.json", 'r') as file:
        json_object = json.load(file)
        rest = json_object['rest']
        return rest['host_prices'] + ":" + rest['port_prices'] + rest['getprices']



if __name__ == "__main__":
    
    conf = json.load(open("config.json"))
    Light = LightController(get_device_url(), get_topic_url(), get_price_url(), conf["mqtt"]["user_id"], conf["mqtt"]["broker"], conf["mqtt"]["port"])
    
    while True:
        Light.control_the_lights()
        time.sleep(1)
        pass
