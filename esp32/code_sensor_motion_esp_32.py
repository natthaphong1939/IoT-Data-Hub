import network
import urequests as requests
import ujson
import machine
import socket
import struct
import time

# กำหนดค่า WiFi
SSID = "***"
PASSWORD = "***"

# API ของ Backend
API_URL = "https://***/motion"

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

# Function to get the current Unix time from an NTP server
def get_ntp_time():
    NTP_DELTA = 2208988800  # NTP time is based on 1900
    ntp_host = "time.nist.gov"

    # Create a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(1)

    # Build NTP request
    data = b'\x1b' + 47 * b'\0'
    address = socket.getaddrinfo(ntp_host, 123)[0][-1]

    try:
        client.sendto(data, address)
        data, _ = client.recvfrom(1024)
        if data:
            t = struct.unpack('!12I', data)[10]
            t -= NTP_DELTA
            return t
    except:
        return None
    finally:
        client.close()

timestamp = get_ntp_time()
if timestamp:
    print("Current Unix Time:", timestamp)
else:
    print("Failed to get NTP time, proceeding with local time.")
    timestamp = int(time.time())

def fetch_count():
    url = "https://***/count"
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
        print("motion detected")

    current_time = time.time()

    # เมื่อครบ 30 นาที ให้ส่งข้อมูล
    if current_time - start_time >= 1800:  # Adjust as needed, seems like it should be 30 based on comment
        json = fetch_count()
        count = json['SyncNumber'] if json else 0  # Add a fallback if fetch_count fails
        print(f"new count ----> {count}")

        # Update timestamp
        timestamp = get_ntp_time()
        if not timestamp:
            timestamp = int(time.time())

        data = {
            "Location": DEVICE_NAME,
            "Timestamp": timestamp,
            "NumberMotion": motion_count,
            "SyncNumber": count
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
