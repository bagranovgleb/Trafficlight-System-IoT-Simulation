import paho.mqtt.client as mqtt
import json
import time
import mysql.connector
from mysql.connector import Error
from pymongo import MongoClient
from neo4j import GraphDatabase
from datetime import datetime

# --- Configuration ---
MYSQL_CONFIG = {
    'host': 'mysql',
    'user': 'dartwind',
    'password': 'cisterntheBasilica1',
    'database': 'smarttrafficlight'
}
MONGO_CONFIG = {
    'host': 'mongo',
    'port': 27017,
    'database': 'traffic_data'
}
NEO4J_CONFIG = {
    'uri': "bolt://neo4j:7687",
    'user': "neo4j",
    'password': "05092004"
}
MQTT_BROKER = "mqtt"
MQTT_PORT = 1883
MQTT_TOPIC = "smart_traffic/intersection_data"


# Global database connections
mysql_conn = None
mysql_cursor = None
mongo_client = None
neo4j_driver = None

def retry_connect_mysql():
    """
    Attempts to connect to the MySQL database with retries.
    Updates global mysql_conn and mysql_cursor.
    Returns True on success, False on failure.
    """
    global mysql_conn, mysql_cursor
    for attempt in range(10):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor(dictionary=True)
            mysql_conn = conn
            mysql_cursor = cursor
            print(f"[OK] MySQL connected on attempt {attempt + 1}")
            return True
        except Error as e:
            print(f"MySQL connection failed: {e}, retrying (attempt {attempt + 1}/10)...")
            time.sleep(3)
    print("MySQL connection failed after multiple attempts.")
    return False

def retry_connect_mongo():
    global mongo_client
    for attempt in range(10):
        try:
            mongo_client = MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'])
            mongo_client.admin.command('ping')
            print(f"[OK] MongoDB connected on attempt {attempt + 1}")
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}, retrying (attempt {attempt + 1}/10)...")
            time.sleep(3)
    print("MongoDB connection failed after multiple attempts.")
    return False

def retry_connect_neo4j():
    global neo4j_driver
    for attempt in range(10):
        try:
            neo4j_driver = GraphDatabase.driver(NEO4J_CONFIG['uri'], auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password']))
            neo4j_driver.verify_connectivity()
            print(f"[OK] Neo4j connected on attempt {attempt + 1}")
            return True
        except Exception as e:
            print(f"Neo4j connection failed: {e}, retrying (attempt {attempt + 1}/10)...")
            time.sleep(3)
    print("Neo4j connection failed after multiple attempts.")
    return False

def get_traffic_light_id(tl_name):
    """Fetches tl_id from MySQL using tl_name."""
    global mysql_conn, mysql_cursor
    if not mysql_conn or not mysql_conn.is_connected():
        print("[ERROR] MySQL connection not active when trying to get tl_id.")
        return None
    try:
        query = "SELECT tl_id FROM trafficlights WHERE tl_name = %s"
        mysql_cursor.execute(query, (tl_name,))
        result = mysql_cursor.fetchone()
        return result['tl_id'] if result else None
    except Exception as e:
        print(f"[ERROR] Failed to get tl_id for {tl_name} from MySQL: {e}")
        return None

def store_sensor_data_in_mongodb(payload):
    """Stores the simplified sensor data in MongoDB."""
    global mongo_client
    if not mongo_client:
        print("[ERROR] MongoDB client not initialized.")
        return

    try:
        db = mongo_client[MONGO_CONFIG['database']]
        collection = db['sensor_readings']

        document = {
            "tl_name": payload.get("tl_name"),
            "timestamp": payload.get("timestamp"),
            "status": payload.get("status")
        }

        if not document["tl_name"]:
            print(f"[WARN] MongoDB: Missing tl_name in payload: {payload}")
            return

        collection.insert_one(document)
        print(f"[MONGO] Stored data for {document['tl_name']} in MongoDB.")
    except Exception as e:
        print(f"[ERROR] Failed to store data in MongoDB: {e}")

def update_traffic_light_status_in_neo4j(tl_id_int, status):
    """Updates the status of a TrafficLight node in Neo4j by managing relationships."""
    global neo4j_driver
    if not neo4j_driver:
        print("[ERROR] Neo4j driver not initialized.")
        return

    try:
        with neo4j_driver.session() as session:
                                                                # MERGE the TrafficLight node to ensure it exists
            session.run("""
                MERGE (tl:TrafficLight {tl_id: $tl_id})
                SET tl.last_updated = datetime()
            """, tl_id=tl_id_int)

                                                                #DETACH DELETE any existing HAS_STATUS relationships for this TrafficLight
            session.run("""
                MATCH (tl:TrafficLight {tl_id: $tl_id})-[r:HAS_STATUS]->(s:Status)
                DELETE r
            """, tl_id=tl_id_int)

                                                                # CREATE a new HAS_STATUS relationship
            session.run("""
                MATCH (tl:TrafficLight {tl_id: $tl_id})
                MERGE (s:Status {name: $status})
                CREATE (tl)-[:HAS_STATUS {timestamp: datetime()}]->(s)
            """, tl_id=tl_id_int, status=status)

            print(f"[NEO4J] Updated status relationship for TrafficLight ID {tl_id_int} to {status}.")
    except Exception as e:
        print(f"[ERROR] Failed to update Neo4j for TrafficLight ID {tl_id_int}: {e}")


def on_message(client, userdata, msg):
    print(f"[{datetime.now()}] [MQTT] Message received: {msg.payload.decode()}")
    try:
        payload = json.loads(msg.payload.decode())

        tl_id_str = payload.get("tl_name")
        status = payload.get("status")

        if not tl_id_str or not status:
            print(f"[{datetime.now()}] [WARN] Incomplete payload: missing 'tl_name' (which is tl_id) or 'status'. Received: {payload}")
            return

        try:
            tl_id_int = int(tl_id_str)
        except ValueError:
            print(f"[{datetime.now()}] [ERROR] Invalid tl_id format: '{tl_id_str}'. Expected a number.")
            return

        store_sensor_data_in_mongodb(payload)
        update_traffic_light_status_in_neo4j(tl_id_int, status)

    except json.JSONDecodeError as e:
        print(f"[{datetime.now()}] [ERROR] Failed to decode JSON from MQTT message: {e}")
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] Error processing MQTT message: {e}")


def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print(f"[{datetime.now()}] [MQTT] Connected with result code {rc}")
        client.subscribe(MQTT_TOPIC)
        print(f"[{datetime.now()}] [MQTT] Subscribed to {MQTT_TOPIC}")
    else:
        print(f"[{datetime.now()}] [MQTT] Failed to connect, return code {rc}")


if __name__ == '__main__':
    print("=== [BOOT] mqtt_handler.py started ===")

    print("[INFO] Connecting to MySQL...")
    if not retry_connect_mysql():
        exit("MySQL connection failed, exiting.")

    print("[INFO] Connecting to MongoDB...")
    if not retry_connect_mongo():
        exit("MongoDB connection failed, exiting.")

    print("[INFO] Connecting to Neo4j...")
    if not retry_connect_neo4j():
        exit("Neo4j connection failed, exiting.")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    print("[DEBUG] Starting MQTT handler setup...")
    print("=== [STEP] MQTT client created ===")
    print("=== [STEP] Attempting connection to broker at mqtt:1883 ===")

    print("[INIT] Waiting 10 seconds for MQTT broker...")
    time.sleep(10)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("[DEBUG] Finished setting up callbacks. Trying to connect...")
        print(f"[DEBUG] Attempting to connect to broker at {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"[FATAL] Failed to connect to MQTT broker: {e}")
        exit(1)

    print("[RUNNING] MQTT handler listening...")
    client.loop_forever()
