import requests

if __name__ == "__main__":
    inp = ""
    while inp != "exit":
        inp = input("Select command: (put/del/get) or exit: ")
        f = inp
        if f == "put":
            # PUT test
            payload = {'deviceType': 'sensor', "id": '330', 'building': 'factory', "floor": '3', "room": '0'}
            r = requests.put('http://127.0.0.1:8080/API/ADDDEVICE', data=payload)

        if f == "del":
            # DELETE test 
            payload = {'deviceType': 'actuator', "id": '30', 'building': 'factory', "floor": '3', "room": '0'}
            r = requests.put('http://127.0.0.1:8080/API/DELDEVICE', data=payload)

        if f == "get":
            # GET test: (getting mqtt config, list of devices etc.)
            payload = {'topics'}
            # payload = {'mqtt-broker'}
            # payload = {'actuators'}
            r = requests.get('http://127.0.0.1:8080/API')#, params=payload)
            print(r.text)



# /API/ADDDEVICE/json: r = requests.get('127.0.0.1:8080/API/ADDDEVICE/', params=payload)
# /API/DELDEVICE/json: r = requests.get('127.0.0.1:8080/API/DELDEVICE/', params=payload)
# /API/DISPLAYDEVICES: r = requests.get('127.0.0.1:8080/API/DISPLAYDEVICES/', params=payload) cherrypy.log(str(params))