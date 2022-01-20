from requests import api
import cherrypy
import json
import requests
import random
from datetime import date


#from jsonhandling import deviceHandler

#docs for requests:
#https://requests.readthedocs.io/en/master/

# >>> payload = {'deviceType': 'sensor', "id": '0', building': 'factory', "floor": '0', "room": '0'}
# For web testing /API/ADDDEVICE?deviceType=sensor&id=2&building=factory&floor=0&room=0
# >>> r = requests.get('127.0.0.1:8080/API/ADDDEVICE/', params=payload)
# /API/ADDDEVICE/json: r = requests.get('127.0.0.1:8080/API/ADDDEVICE/', params=payload)
# /API/DELDEVICE/json: r = requests.get('127.0.0.1:8080/API/DELDEVICE/', params=payload)
# /API/DISPLAYDEVICES: r = requests.get('127.0.0.1:8080/API/DISPLAYDEVICES/', params=payload) cherrypy.log(str(params))

class EnergyPricesAPI:
    exposed=True

    __average_price = 0.2192 # average price as of 14/01/2022 https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Electricity_price_statistics
    __price_max_var = 0.05 # maximum variance of the price
    __currency = "EUR"

    def GET(self,*uri,**params):
		
        if len(uri) > 0:
            if uri[0].lower() == "get":
                if uri[1].lower() == "prices":
                    return self.energy_price_json(self.current_energy_price())
                
                # for simulation purposes
                if uri[1].lower() == "lowprices":
                    return self.energy_price_json(self.low_energy_price())
                if uri[1].lower() == "highprices":
                    return self.energy_price_json(self.high_energy_price())
    
            
    def energy_price_json(self, prices):
        json_string = {
           'price_in_kWh': round(prices,3),
           'currency': self.__currency,
           'date': date.today().strftime("%d/%m/%Y")
        }
        return json.dumps(json_string)
        
    def current_energy_price(self):
        return self.__average_price + (random.random()*2-1)*self.__price_max_var

    def high_energy_price(self):
        return self.__average_price + random.random()*self.__price_max_var

    def low_energy_price(self):
        return self.__average_price - random.random()*self.__price_max_var
    

if __name__=="__main__":
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 9090})
    conf={
		'/':{
			'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on':True,
		}
    }
    cherrypy.tree.mount(EnergyPricesAPI(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()

  