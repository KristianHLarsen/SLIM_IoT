import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
import re


class SlimBot:
    def __init__(self):
        # Catalog token
        config = json.load(open("config.json"))
        self.tokenBot = config["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()
 
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = str(msg['text'])

        # Extract command from message
        command = message.split(" ")[0]
        # Remove the command string from the message
        message = re.sub(command, '', message)
        if command == "/addDevice":
            payload = self.format_msg_to_json(message)
            r = requests.put('http://172.15.10.20:8080/api/adddevice', data=payload)
            self.bot.sendMessage(chat_ID, text=str(r.text))

        elif command == "/removeDevice":
            payload = self.format_msg_to_json(message)
            r = requests.put('http://172.15.10.20:8080/api/deldevice', data=payload)
            self.bot.sendMessage(chat_ID, text= r.text)

        elif command == "/graphs":
            output = "http://0.0.0.0:8080/graphs"
            self.bot.sendMessage(chat_ID, text=output)

        elif command == "/deviceLocations":
            output = "http://0.0.0.0:8080/devices"
            self.bot.sendMessage(chat_ID, text=output)

        elif command == "/start":
            self.bot.sendMessage(chat_ID, text="Available commands: /graphs, /addDevice, /removeDevice, /deviceLocations")
            msg_format1 = '/addDevice deviceType=sensor, id=10, building=main, floor=4, room=3'
            msg_format2 = '/removeDevice deviceType=actuator, id=11, building=main, floor=4, room=3'
            self.bot.sendMessage(chat_ID, text="To add/remove device:\n" + msg_format1 + "\n" + msg_format2)
        else:
            self.bot.sendMessage(chat_ID, text="Available commands: /graphs, /addDevice, /removeDevice, /deviceLocations")
            msg_format1 = '/addDevice deviceType=sensor, id=10, building=main, floor=4, room=3'
            msg_format2 = '/removeDevice deviceType=actuator, id=11, building=main, floor=4, room=3'
            self.bot.sendMessage(chat_ID, text="To add/remove device:\n" + msg_format1 + "\n" + msg_format2)

    def format_msg_to_json(self, message):
        # NOTE: format of message must be:
        # /addDevice deviceType = sensor, id = 10, building = main, floor = 4, room = 3
        # (whitespace is optional)
        #        
        # Remove all whitespace from message
        params = re.sub(' ', '', message)
        # Format it into json
        params = '{"' + params + '"}'
        params = re.sub('=', '": "', params)
        params = re.sub(',', '", "', params)
        payload = json.loads(params)
        return payload