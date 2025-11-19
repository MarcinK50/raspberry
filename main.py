import utime, network, dht, mrequests as requests
from machine import Pin, UART
from pms5003 import PMS5003
import config

location = 'pokoj'
ssid = config.ssid
password = config.password
ip, port = config.server_ip, config.server_port

lat = config.lat
lon = config.lon

url = f"http://{ip}:{port}/exec"
update_rate = 15

power_led = Pin(10, Pin.OUT)
wifi_led = Pin(11, Pin.OUT)
data_led = Pin(12, Pin.OUT)
power_led.value(0)
wifi_led.value(0)
data_led.value(0)

sensor = dht.DHT22(Pin(16))
pms5003 = PMS5003(
    uart=UART(1, tx=Pin(8), rx=Pin(9), baudrate=9600),
    pin_enable=Pin(3),
    pin_reset=Pin(2),
    mode="active"
)

if config.status_led: power_led.value(1)


def connect_to_wifi(ssid,password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('Laczenie.....')
        utime.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('Blad polaczenia')
    else:
        print('Pomyslnie polaczono!')
        if config.status_led: wifi_led.value(1)
        network_info = wlan.ifconfig()
        print('IP:', network_info[0])
        #ntptime.host = "tempus1.gum.gov.pl"
        #ntptime.settime()
       
def get_temperature():
    try:
        data = sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print('reading dht22 success')
        file = open('dht22.txt', "w")
        file.write(f'{temp}, {hum}')
        file.close()
        print([temp,hum])
        return [temp, hum]
    except:
        print('error reading dht22!')
        return ['NULL', 'NULL']

def get_pollution():
    try:
        pms = pms5003.read()
        pm1 = pms.data[0]
        pm25 = pms.data[1]
        pm10 = pms.data[2]
        print('reading pms5003 success')
        file = open('pms5003.txt', "w")
        file.write(f'{pm1}, {pm25}, {pm10}')
        file.close()
        print([pm1, pm25, pm10])
        return [pm1, pm25, pm10]
    except:
        print('error reading pms5003!')
        return ['NULL', 'NULL', 'NULL']

def url_encode(string):
    encoded_string = ''
    for char in string:
        if char.isalpha() or char.isdigit() or char in '-._~':
            encoded_string += char
        else:
            encoded_string += '%' + '{:02X}'.format(ord(char))
    return encoded_string

def send_results(location,temperature, humidity, pm1, pm25, pm10):
    query = f"INSERT INTO sensors(id,lat,lng,temperature,humidity,pm1,pm25,pm10,timestamp) VALUES('{location}',{str(lat)},{str(lon)},{str(temperature)},{str(humidity)},{str(pm1)},{str(pm25)},{str(pm10)},systimestamp())"
    full_url = url+"?query="+url_encode(query)
    
    try:
        requests.get(url=full_url, auth=(config.questdb_user, config.questdb_password))
        return 0
    except Exception as error:
        if str(error) == "unsupported types for __add__: 'str', 'bytes'": return 0
        else: return 1

def main():
  connect_to_wifi(ssid,password)
  while True:
    temperature, humidity = get_temperature()
    pm1, pm25, pm10 = get_pollution()
    response = send_results(location,temperature, humidity, pm1, pm25, pm10)
    while response != 0:
        response = send_results(location,temperature, humidity, pm1, pm25, pm10)
        print(response)
        utime.sleep(1)
    if config.status_led:
        data_led.value(1)
        utime.sleep(1)
        data_led.value(0)
    utime.sleep(update_rate)

main()