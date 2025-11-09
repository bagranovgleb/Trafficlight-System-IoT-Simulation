## 🚦 Smart Traffic Management System

A **Smart Traffic Management System** designed to monitor traffic lights using real-time simulated IoT data.  
This project integrates **Flask**, **MQTT**, **MySQL**, **MongoDB**, and **Neo4j** inside a **Docker-based microservice environment**.

______________________________________________

## 👓 Overview

This system simulates IoT-based traffic sensors that send vehicle data through MQTT.  
The received data is processed and stored across different databases:

- **MySQL** – stores structured traffic light and intersection metadata  
- **MongoDB** – stores real-time and historical traffic sensor data  
- **Neo4j** – maintains graph-based relationships between intersections and updates traffic light states  
- **MQTT Broker** – manages IoT data exchange  
- **Flask Web App** – displays live traffic light statuses and system insights

______________________________________________

## 📒 Instructions to start through Docker

----------------------------------------------
# ❗ Make sure you have these installed:

Docker Desktop
Docker Compose
A terminal or Git Bash

----------------------------------------------


Step 1:
Use Git Bash to cd in smart_traffic_system folder


Step 2:
In Git Bash:  ```docker-compose up --build```


Step 3:
When everything is fine you will see this text:
```text
Flask app running on http://0.0.0.0:5000
Connected to Neo4j
MQTT connected on port 1883```


Step 4:
Go to ```http://localhost:5000```


>🧰 To stop Docker use: ```docker-compose down```

______________________________________________

##🔌 Ports

| Service       | Default Port | Description         |
| ------------- | ------------ | ------------------- |
| Flask App     | `5000`       | Web dashboard       |
| MQTT Broker   | `1883`       | Message exchange    |
| MySQL         | `3306`       | Structured data     |
| MongoDB       | `27017`      | Traffic sensor data |
| Neo4j Browser | `7474`       | Graph visualization |

______________________________________________

## 🧱 System Architecture

``` <pre>
C:.
│   docker-compose.yml
│   Plan.png
│   project ideas.txt
│   requirements.txt
│
├───app
│   │   app.py
│   │   config.py
│   │   Dockerfile
│   │   requirements.txt
│   │
│   ├───db
│   │   │   neo4j_utils.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           neo4j_utils.cpython-313.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───routes
│   │   │   tl_status.py
│   │   │   __init__.py
│   │   │
│   │   └───__pycache__
│   │           tl_status.cpython-313.pyc
│   │           __init__.cpython-313.pyc
│   │
│   ├───static
│   │   └───css
│   │           style.css
│   │
│   ├───templates
│   │       traffic_light_status.html
│   │
│   └───__pycache__
│           config.cpython-313.pyc
│
├───mosquitto
│   ├───config
│   │       mosquitto.conf
│   │
│   ├───data
│   └───log
├───mqtt_handler
│   │   config.py
│   │   Dockerfile
│   │   mqtt_handler.py
│   │   requirements.txt
│   │
│   └───__pycache__
│           config.cpython-310.pyc
│
├───mqtt_simulator
│       config.py
│       Dockerfile
│       requirements.txt
│       simulate_iot.py
│
├───mysql_populator
│   │   config.py
│   │   Dockerfile
│   │   populate_mysql.py
│   │
│   └───__pycache__
│           config.cpython-310.pyc
│
└───neo4j_populator
    │   config.py
    │   Dockerfile
    │   populate_neo4j.py
    │
    └───__pycache__
            config.cpython-310.pyc
</pre>```
