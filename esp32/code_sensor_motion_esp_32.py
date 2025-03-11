import network
import urequests as requests
import ujson
import machine
import time

# กำหนดค่า WiFi
SSID = "***"
PASSWORD = "***"

# API ของ Backend
API_URL = "http://*****:8000/motion"

# ตั้งค่า PIR Sensor (ขา GPIO14 หรือ D5 บน ESP8266/ESP32)
pir_pin = machine.Pin(14, machine.Pin.IN)

# ตั้งค่าชื่อของอุปกรณ์นี้ (เปลี่ยนตามอุปกรณ์จริง)
DEVICE_NAME = "sensor1"  # เปลี่ยนเป็น sensor2, sensor3 บนอุปกรณ์อื่น

# เชื่อมต่อ Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

while not station.isconnected():
    print("Connecting to WiFi...")
    time.sleep(1)

print("Connected! IP Address:", station.ifconfig())

# ตัวแปรเก็บจำนวนการเคลื่อนไหว
motion_count = 0
start_time = time.time()

def fetch_count():
    url = "http://172.20.10.2:8000/count"
    try:
        response = requests.get(url)
        count_data = response.json()
        print(count_data)
        response.close()  
        return count_data
    except Exception as e:
        print("Error:", e)
        return None


while True:
    if pir_pin.value() == 1:
        motion_count += 1
        print("count")

    current_time = time.time()

    # เมื่อครบ 30 วินาที ให้ส่งข้อมูล
    if current_time - start_time >= 10:
        json = fetch_count()
        count = json['count']
        print(f"new count ----> {count}")
        timestamp = int(time.time())  # ได้เป็น Unix Timestamp

        data = {
            "Location": DEVICE_NAME,
            "Timestamp": timestamp,
            "NumberMotion": motion_count,
            "SyncNumber" : count
        }
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(API_URL, data=ujson.dumps(data), headers=headers)
            print("Sent:", data, "Response:", response.text)
        except Exception as e:
            print("Failed to send data:", e)

        # รีเซ็ตตัวนับ
        motion_count = 0
        start_time = current_time

    time.sleep(1)  # ตรวจสอบทุก 1 วินาที

