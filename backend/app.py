from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from psycopg2 import pool, sql
import os
import psycopg2
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()


DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

try:
    conn_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
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
    

@app.post('/temp')
async def post_temp(tempdata: TempData) -> dict:
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO temperature_logs (location, timestamps, temperature)
            VALUES (%s, %s, %s)
        """)
        cur.execute(insert_query, (tempdata.Location, tempdata.Timestamp, tempdata.Temperature))
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(tempdata.Timestamp))
        return {"message": "Done JA", "timestamp": dt}
    except Exception as e:
        logger.error(f"Failed to post temperature data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        cur.close()

@app.post('/motion')
async def post_motion(motiondata: MotionData) -> dict:
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        insert_query = sql.SQL("""
            INSERT INTO motion_logs  (location, timestamps, Number_of_movements)
            VALUES (%s, %s, %s)
        """)
        # Number_of_movements --> Number of captured movements/30min
        cur.execute(insert_query, (motiondata.Location, motiondata.Timestamp, motiondata.NumberMotion))
        dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(motiondata.Timestamp))
        return {"message": "Done JA", "timestamp": dt}
    except Exception as e:
        logger.error(f"Failed to post motion sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        cur.close()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
