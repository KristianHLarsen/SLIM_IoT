from thingspeak_adapter import ThingspeakAdaptor
import time
import requests

def update():
    
    for x in range(0,15):            
        tsAdaptor.updateActiveTime()
        # Get current energy prices
        if x >= 14:
            costs, consumption, price = tsAdaptor.calculateEnergyAndCosts()
        time.sleep(1)
    return costs, consumption, price

if __name__ == "__main__":
    tsAdaptor = ThingspeakAdaptor("ts_adaptor")
    while True:        
        energy_costs, energy_consumption, price_in_kWh = update()
        tsAdaptor.ts_update("Energy costs", energy_costs)
        energy_costs, energy_consumption, price_in_kWh = update()
        tsAdaptor.ts_update("Energy prices", price_in_kWh)
        energy_costs, energy_consumption, price_in_kWh = update()
        tsAdaptor.ts_update("Energy consumption", energy_consumption)
        

