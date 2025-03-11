# IoT-Data-Hub

This project is used for the **EN814710 Cloud Application and Networking** course.  
It collects temperature data via the **AM2301A** sensor and detects movement using the **HC-SR501** sensor, all connected to an **ESP32**.  

The system measures indoor and outdoor temperatures to check if the air conditioner is running efficiently and if the room is occupied. It sends notifications to the professor’s page approximately **every 30 minutes**.

---

## Requirement  

### Hardware  
- **AM2301A** – 2 units  
- **HC-SR501** – As needed  
- **ESP WEMOS D1 (ESP-WROOM-32)** – 2 or more units  

### Software  
- **Docker Compose** – Version **3.8**  
- **Docker** – Version **24.0.7+**  

---

## Deployment Instructions  

### Starting the Docker Containers  
Run the following command to build and start the containers:  
```sh
docker-compose up --build
```

### Stopping the Docker Containers
To stop the containers, use:
```sh
docker-compose down  # Add `-v` to remove volumes if necessary
```

---
## Important Notes

⚠️ **WARNING!** Before using this project, make sure to set the `DEVICE_TEMP` to be the same as `Location` in the ESP32 code. I highly recommended to create and configure a default `.env` file with the appropriate settings for `DEVICE_TEMP` and `Location`.

