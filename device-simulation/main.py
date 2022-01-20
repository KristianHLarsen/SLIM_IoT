from SensorHandler import SensorHandler
from ActuatorHandler import ActuatorHandler
import requests
import threading, time
if __name__ == "__main__":
    time.sleep(10)
    sensorHandler = SensorHandler()
    actuatorHandler = ActuatorHandler()
    # Counter to periodically check if new topics have been added
    counter = 0
    # How often (in seconds) to publish sensor data
    publish_interval = 20
    while True:
        sensorHandler.updateSensorTopics()
        actuatorHandler.updateActuatorTopics()
        if counter == 0 or counter >= publish_interval:
            sensorHandler.send()
        time.sleep(5)
        counter += 5
        
        