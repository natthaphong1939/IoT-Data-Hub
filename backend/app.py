from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from psycopg2 import pool, sql
from datetime import datetime
from dotenv import load_dotenv
import os
import psycopg2
import logging
import asyncio

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()


DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
device1 = os.getenv("DEVICE1")
device2 = os.getenv("DEVICE2")

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


class TempData(BaseModel):
    Location: str
    Timestamp: int
    Temperature: float


class MotionData(BaseModel):
    Location: str 
    Timestamp:int
    NumberMotion:int


async def currentTime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def query(var: str, tempP: float,timeP: int):
    conn = get_db_connection()  
    query = """
    SELECT timestamps, temperature
    FROM temperature_logs
    WHERE location = %s
    AND timestamps = (SELECT MAX(timestamps) FROM temperature_logs WHERE location = %s);
    """
    result = await asyncio.to_thread(execute_query, conn, query, var)
    if result:
        timestampOld, temperatureOld = result[0], result[1]
        if abs(float(temperatureOld) - tempP) > 10 and abs(timestampOld-timeP) < 25:
            print(f"Noone here naja")
        else :
            print("ARA-ARA it's normally, Good boy.")
    else:
        print("No data found.")
    conn_pool.putconn(conn)

def execute_query(conn, query, var):
    with conn.cursor() as cursor:
        cursor.execute(query, (var, var))
        return cursor.fetchone()  
        

@app.post('/temp')
async def post_temp(tempdata: TempData) -> dict:
    conn = None
    #Before test you need to change the "Location" in .env file
    if tempdata.Location == device1:
        await query(device2,tempdata.Temperature,tempdata.Timestamp)
    if tempdata.Location == device2:
        await query(device1,tempdata.Temperature,tempdata.Timestamp)
    try:
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
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    finally:
        if conn:
            conn_pool.putconn(conn)  

@app.post('/motion')
async def post_motion(motiondata: MotionData) -> dict:
    conn = None
    try:
        conn = get_db_connection()  
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO motion_logs  (location, timestamps, Number_of_movements)
                VALUES (%s, %s, %s)
            """
            cur.execute(insert_query, (motiondata.Location, motiondata.Timestamp, motiondata.NumberMotion))
        return {"message": "Motion Sensor data logged successfully.", "timestamp": await currentTime()}
    except Exception as e:
        logger.error(f"Failed to post motion sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        if conn:
            conn_pool.putconn(conn) 


@app.get("/")
async def read_root():
    return {"Hello": "World"}
