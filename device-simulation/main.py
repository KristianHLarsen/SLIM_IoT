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
    # How often (in seconds) to check for new topics
    update_interval = 5
    while True:
        sensorHandler.send()
        time.sleep(20)
        sensorHandler.updateSensorTopics()
        actuatorHandler.updateActuatorTopics()
        