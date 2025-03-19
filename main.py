from machine import Pin, RTC
import dht
from time import sleep
import network
import ntptime
import secret

ssid = secret.ssid
password = secret.password

# Init Wi-Fi Interface
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Connect to your network
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Laczenie.....')
    sleep(1)

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Blad polaczenia')
else:
    print('Pomyslnie polaczono!')
    network_info = wlan.ifconfig()
    print('IP:', network_info[0])
    ntptime.host = "tempus1.gum.gov.pl"
    ntptime.settime()

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
    data["time"] = f"{RTC().datetime()[4]+1}:{RTC().datetime()[5]}:{RTC().datetime()[6]}" # TODO: godzina w RTC jest w UTC; trzeba przesunac zgodnie z strefa
    data["temp"] = temp
    data["hum"] = hum
    SaveIniFile("/dane.txt", data)
  except OSError as e:
    print('Failed to read sensor.')