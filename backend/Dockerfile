FROM python:3.11

RUN apt-get update && apt-get install -y nano

WORKDIR /app
COPY app.py /app/
COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
