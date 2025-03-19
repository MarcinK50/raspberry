from machine import Pin
import dht
from time import sleep

sensor = dht.DHT22(Pin(16))

while True:
  try:
    sleep(2)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    print('Temperatura: %3.1f C' %temp)
    print('Wilgotnosc: %3.1f %%' %hum)
  except OSError as e:
    print('Failed to read sensor.')