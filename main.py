from machine import Pin, RTC
import dht
from time import sleep

sensor = dht.DHT22(Pin(16))

def SaveIniFile(filename, dictionary):
    with open(filename, "a") as f:
        for key in dictionary:
            f.write(f'{dictionary["time"]};{dictionary["temp"]};{dictionary["hum"]}\n')
            
def LoadIniFile(filename):
    dictionary = {}
    with open(filename, "r") as f:
        for s in f:
            lst = s.strip().split(",")
            dictionary[lst[0]] = lst[1]
    return dictionary

while True:
  try:
    sleep(2)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print('Temperatura: %3.1f C' %temp)
    print('Wilgotnosc: %3.1f %%' %hum)
    print(f'{RTC().datetime()}\n')
    data = {}
    data["time"] = f"{RTC().datetime()[4]}:{RTC().datetime()[5]}:{RTC().datetime()[6]}"
    data["temp"] = temp
    data["hum"] = hum
    SaveIniFile("/MyData.txt", data)
  except OSError as e:
    print('Failed to read sensor.')