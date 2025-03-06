import os
import logging
import asyncio
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from psycopg2 import pool, sql

# Load environment variables from the .env file
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Database connection details from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Assign locations for the devices from environment variables
device1 = os.getenv("DEVICE_TEMP1")
device2 = os.getenv("DEVICE_TEMP2")

#number of Motion Sensors
numberMotion = os.getenv("MOTION_SENSOR_COUNT")

#Temperature difference (Celsius)
temp_diff = 10 

#Time difference (Second Unit)
time_diff = 25

#Use to sync motion sensor
count = 0



class TempData(BaseModel):
    Location: str
    Timestamp: int
    Temperature: float

class MotionData(BaseModel):
    Location: str 
    Timestamp:int
    NumberMotion:int
    SyncNumber:int

try:
    conn_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=3,
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    logger.info("Database connection pool created successfully.")
except Exception as e:
    logger.error(f"Error creating connection pool: {str(e)}")
    raise

def get_db_connection():
    try:
        conn = conn_pool.getconn()
        conn.autocommit = True
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise RuntimeError("Database connection error.")

async def currentTime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def query(secondary_device: str, current_temperature: float,current_timestamp: int):
    conn = get_db_connection()
    # Query the latest data of the secondary device to compare with the incoming data
    query = """
    SELECT timestamps, temperature
    FROM temperature_logs
    WHERE location = %s
    AND timestamps = (SELECT MAX(timestamps) FROM temperature_logs WHERE location = %s);
    """
    result = await asyncio.to_thread(execute_query, conn, query, secondary_device)
    if result:
        previous_timestamp, previous_temperature = result[0], result[1]
        # If the temperature difference exceeds 10 and the time difference is less than 25 seconds, trigger an alert
        if abs(float(previous_temperature) - current_temperature) > temp_diff and abs(previous_timestamp - current_timestamp) < time_diff:
            print(f"No one is here. The air conditioner should turn off.")  # Trigger alert
    conn_pool.putconn(conn)

def execute_query(conn, query, secondary_device):
    with conn.cursor() as cursor:
        cursor.execute(query, (secondary_device, secondary_device))
        return cursor.fetchone()  

@app.get("/temp")
async def get_temp1():
    conn = None
    try:
        conn = conn_pool.getconn()
        with conn.cursor() as cur:
            query = """
            SELECT DISTINCT ON (location) 
            location, timestamps, CAST(temperature AS DOUBLE PRECISION) AS temperature
            FROM temperature_logs
            ORDER BY location, timestamps DESC;
            """
            cur.execute(query)
            data = cur.fetchall()            
            json_data = {
                row[0]: {"Location": row[0], "Timestamps": row[1], "Temperature": row[2]}
                for row in data
            }
        return json_data
    except Exception as e:
        logger.error(f"Failed to fetch temperature data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn)

# Handles HTTP POST requests to compare the request before logging temperature data into the database.
@app.post('/temp')
async def post_temp(tempdata: TempData) -> dict:
    conn = None
    try:
        # Before testing, change the "Location" (Name of the device) in .env file
        secondary_device = None
        if tempdata.Location == device1:
            secondary_device = device2
        elif tempdata.Location == device2:
            secondary_device = device1
        else:
            logger.error("Unknown device location provided.")
            raise HTTPException(status_code=400, detail="Unknown device location provided.")

        await query(secondary_device, tempdata.Temperature, tempdata.Timestamp)

        conn = get_db_connection()  
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO temperature_logs (location, timestamps, temperature)
                VALUES (%s, %s, %s)
            """
            cur.execute(insert_query, (tempdata.Location, tempdata.Timestamp, tempdata.Temperature))

        return {"message": "Temperature Sensor data logged successfully.", "timestamp": await currentTime()}
    except Exception as e:
        logger.error(f"Failed to post temperature data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn)

@app.get('/motion1')
async def get_motion():
    conn == None
    try:
        conn = get_db_connection()


    except Exception as e:
        logger.error(f"Failed to fetch temperature data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn)

# Handles HTTP POST requests to log motion sensor data into the database
@app.post('/motion')
async def post_motion(motiondata: MotionData) -> dict:
    conn = None
    try:
        conn = get_db_connection()  
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO motion_logs  (location, timestamps, Number_of_movements)
                VALUES (%s, %s, %s.%s)
            """
            cur.execute(insert_query, (motiondata.Location, motiondata.Timestamp, motiondata.NumberMotion, motiondata.SyncNumber))
        return {"message": "Motion Sensor data logged successfully.", "timestamp": await currentTime()}
    except Exception as e:
        logger.error(f"Failed to post motion sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn)

@app.get('/motion')
async def get_motion():
    conn = None
    try:
        conn = conn_pool.getconn()
        with conn.cursor() as cur:
            query = """
            SELECT location, timestamps, Number_of_movements
            FROM motion_logs
            ORDER BY timestamps DESC;
            """
            cur.execute(query)
            data = cur.fetchall()
            json_data = [
                {"Location": row[0], "Timestamp": row[1], "Number_of_movements": row[2]}
                for row in data
            ]
        return {"motion_logs": json_data}
    except Exception as e:
        logger.error(f"Failed to fetch motion data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn) 

#Every 25 minute it will increment count 1
@app.get('/count')
async def get_count():
    int count = 0
    while True:
        await asyncio.sleep(25 * 60)  # Sleep for 25 minutes
        count += 1
    return {"count": count}

@app.on_event("startup")
@repeat_every(seconds=25 * 60)  # Repeat every 25 minutes
async def increment_count_task() -> None:
    global count
    count += 1

@app.get('/count')
async def get_count():
    return {"Count": count}

#Just a Root path Nothing importance :)
@app.get("/")
async def read_root():
    return {"Hello": "World"}
