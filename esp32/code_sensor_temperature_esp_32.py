from machine import Pin
import network
import urequests 
import dht
import utime
import ujson

#Pin
PIN_DHT = const(**)
DHT_Sensor = dht.DHT22(Pin(PIN_DHT))  

#time
EPOCH_OFFSET = const(946684800)

#Wi-FI Credentials
SSID = const("**") #SSID Wifi
PASSWORD = const("*******") #Password wifi

#URL Back-end
URL = const("https://*********/temp") 
headers = {'Content-Type': 'application/json'}

try:
    sta_if = network.WLAN(network.STA_IF) #statation interface
    sta_if.active(True)
    sta_if.connect(SSID, PASSWORD)
except Exception as e:
    print(str(e))
    
while not sta_if.isconnected():
    print("Connecting to Wi-Fi... Naja")
    utime.sleep(1)
print("Connected\n This board IP is --> ", sta_if.ifconfig()[0])

#Measure a temperature 
def read_data() -> dict:
    current_Measuretime = utime.time() + EPOCH_OFFSET
    try:
        DHT_Sensor.measure()
        temp = DHT_Sensor.temperature()
        sensor_data = {
            "Location" : "Inside", #This board's position. You must use "Inside" and "Outside" only. 
            "Timestamp": current_Measuretime,
            "Temperature": temp,
        }
    except Exception as e:
        sensor_data = {
            "Location" : "Inside", #This board's position. You must use "Inside" and "Outside" only. 
            "Timestamp": current_Measuretime,
            "Temperature": None
            }
    return ujson.dumps(sensor_data)

#Post data to a server
def post_data(json_data) :
    try:
        response = urequests.post(URL, data=json_data, headers=headers)
        print("POST status code:", response.status_code)
        print("POST response text:", response.text)
    except Exception as e:
        print(str(e))

while  True:
    json_data = read_data()
    post_data(json_data)
    utime.sleep(1800) #sleep 30 minutes

