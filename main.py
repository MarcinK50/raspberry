import utime, network, dht, mrequests as requests
from machine import Pin, UART
from pms5003 import PMS5003
import config
import ubinascii

DO_DEBUG = True

SSID = config.ssid
PASSWORD = config.password
QUESTDB_USER = config.questdb_user
QUESTDB_PASSWORD = config.questdb_password

ID = config.location_id
IP, PORT = config.server_ip, config.server_port
UPDATE_RATE = config.update_rate
lat = config.lat
lon = config.lon
url = f"http://{IP}:{PORT}/exec"

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
    if DO_DEBUG:
        print('SSID: ', ssid)
        print('Pass: ', password)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if DO_DEBUG:    
        mac = ubinascii.hexlify(wlan.config('mac'),':').decode()
        print('MAC: ', mac)
        for w in wlan.scan():
            print(' * ', w[0].decode())        
    
    wlan.connect(SSID, PASSWORD)
    connection_timeout = config.wifi_timeout
    print('Connecting', end='')
    while connection_timeout > 0:
        if wlan.status() >= 3:
            break
        connection_timeout -= 1
        print('.', end='')
        utime.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('Connection error')
    else:
        print('Connection successful!')
        if config.status_led: wifi_led.value(1)
        network_info = wlan.ifconfig()
        if DO_DEBUG:
            print('IP:', network_info[0])
            
        #ntptime.host = "tempus1.gum.gov.pl"
        #ntptime.settime()
       
def get_temperature():
    try:
        data = sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        print('Reading dht22 success')
        file = open('dht22.txt', "w")
        file.write(f'{temp}, {hum}') # Add timestamp to log
        file.close()
        print([temp,hum])
        return [temp, hum]
    except:
        print('Error reading dht22!')
        return ['NULL', 'NULL']

def get_pollution():
    try:
        pms = pms5003.read()
        pm1 = pms.data[0]
        pm25 = pms.data[1]
        pm10 = pms.data[2]
        print('Reading pms5003 success') 
        file = open('pms5003.txt', "w")
        file.write(f'{pm1}, {pm25}, {pm10}') # Add timestamp to log
        file.close()
        print([pm1, pm25, pm10])
        return [pm1, pm25, pm10]
    except:
        print('Rrror reading pms5003!')
        return ['NULL', 'NULL', 'NULL']

def url_encode(string):
    encoded_string = ''
    for char in string:
        if char.isalpha() or char.isdigit() or char in '-._~':
            encoded_string += char
        else:
            encoded_string += '%' + '{:02X}'.format(ord(char))
    return encoded_string

def send_results(ID,temperature, humidity, pm1, pm25, pm10):
    # TODO: Don't send lat, lng into database rows. Make it separate.
    query = f"INSERT INTO sensors(id,temperature,humidity,pm1,pm25,pm10,timestamp) VALUES('{ID}',{str(temperature)},{str(humidity)},{str(pm1)},{str(pm25)},{str(pm10)},systimestamp())"
    full_url = url+"?query="+url_encode(query)
    
    
    if DO_DEBUG:
        print("Executing query : ")
        print(full_url)
    
    try:
        requests.get(url=full_url, auth=(QUESTDB_USER, QUESTDB_PASSWORD))
        return 0
    except Exception as error:
        if str(error) == "Unsupported types for __add__: 'str', 'bytes'": return 0
        else:
            print("General error: ",str(error))
            return 1

def main():
    connect_to_wifi(SSID,PASSWORD)
    while True:
        temperature, humidity = get_temperature()
        pm1, pm25, pm10 = get_pollution()
        response = send_results(ID,temperature, humidity, pm1, pm25, pm10)
        while response != 0:
            response = send_results(ID,temperature, humidity, pm1, pm25, pm10)
            print("Sending : ",response)
            utime.sleep(1)
        if config.status_led:
            data_led.value(1)
            utime.sleep(1)
            data_led.value(0)
        
        utime.sleep(UPDATE_RATE)

main()
