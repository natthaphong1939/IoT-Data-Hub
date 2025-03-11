import os
import json
import logging
import asyncio
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel
from psycopg2 import pool
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection details from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

# Assign locations for the devices from environment variables
device1 = os.getenv("DEVICE_TEMP1")
device2 = os.getenv("DEVICE_TEMP2")

#Temperature difference (Celsius)
temp_diff = float(10)

#Time difference (Second Unit)
time_diff = 180

#Use to sync motion sensor
app.state.sync_count = 0
app.state.i = 0

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

async def query(secondary_device: str, current_temperature: float, current_timestamp: int):
    try:
        app.state.i = app.state.i +1
        if app.state.i == 2:
            conn = get_db_connection()
            query = """
            SELECT timestamps, temperature
            FROM temperature_logs
            WHERE location = %s
            ORDER BY timestamps DESC
            LIMIT 1;
            """ 
            with conn.cursor() as cursor:
                cursor.execute(query, (secondary_device,))
                result = cursor.fetchone()
            app.state.i = 0
            if result:
                previous_timestamp, previous_temperature = result
                # If the temperature difference exceeds 10 and the time difference is less than 1500 seconds(25 minutes), trigger an alert
                if (
                    abs(float(previous_temperature) - float(current_temperature)) > temp_diff and
                    abs(previous_timestamp - current_timestamp) < time_diff
                ):
                    logger.warning("No one is here. The air conditioner should turn off. -- 1") # Trigger alert
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        conn_pool.putconn(conn)

def getMotionData(sync_number: int, group: bool = False):
    conn = get_db_connection()
    try:
        if group:
            query = """
            SELECT SUM(numberOfMovements), MAX(timestamps)
            FROM motion_logs
            WHERE syncNumber = %s;
            """
        else:
            query = """
            SELECT location, timestamps, numberOfMovements
            FROM motion_logs
            WHERE syncNumber = %s;
            """
        with conn.cursor() as cur:
            cur.execute(query, (sync_number,))
            data = cur.fetchall()
        if group:
            total_movements, max_timestamp = data[0] if data else (0, None)
            if total_movements == 0:
            return {
                "totalMovements": total_movements,
                "maxTimestamp": max_timestamp if max_timestamp else "No data"
            }
        else:
            return {
                row[0]: {"Location": row[0], "Timestamp": row[1], "NumberOfMovements": row[2]}
                for row in data
            }
    except Exception as e:
        logger.error(f"Failed to fetch motion data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn)  

@app.get('/motion/each')
async def get_each_motion():
    return  getMotionData(app.state.sync_count , group=False)

@app.get('/motion/group')
async def get_group_motion():
    return  getMotionData(app.state.sync_count , group=True)

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

# Handles HTTP POST requests to log motion sensor data into the database
@app.post('/motion')
async def post_motion(motiondata: MotionData) -> dict:
    conn = None
    try:
        conn = get_db_connection()  
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO motion_logs (location, timestamps, numberOfMovements, syncNumber)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(insert_query, (motiondata.Location, motiondata.Timestamp, motiondata.NumberMotion, motiondata.SyncNumber))
        return {"message": "Motion Sensor data logged successfully.", "timestamp": await currentTime()}
    except Exception as e:
        logger.error(f"Failed to post motion sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error")
    finally:
        if conn:
            conn_pool.putconn(conn)

@app.get('/count')
async def get_count():
    return {"SyncNumber": app.state.sync_count}

#Just a Root path Nothing importance :)
@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.on_event("startup")
@repeat_every(seconds=25 * 60)  # Repeat every 25 minutes
async def increment_count_task():
    app.state.sync_count += 1
    if app.state.sync_count  > 15:
        app.state.sync_count  = 0
    
@app.on_event("startup")
@repeat_every(seconds=31*60) #Repeat every 31 minutes
async def check_motion() -> None:   
    totalMove = getMotionData(app.state.sync_count , group=True)
    if (totalMove == 0):
        logger.warning("No one is here. The air conditioner should turn off. --3") # Trigger alert
    
