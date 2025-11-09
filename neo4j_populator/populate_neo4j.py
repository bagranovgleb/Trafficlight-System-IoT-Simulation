import time
import mysql.connector
from mysql.connector import Error
from py2neo import Graph, Node, Relationship
from config import MYSQL_CONFIG, NEO4J_CONFIG
import random

# === Wait for MySQL and Table ===
def wait_for_mysql_and_table():
    for attempt in range(10):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SHOW TABLES LIKE 'trafficlights'")
            if cursor.fetchone():
                print("[OK] Connected to MySQL and found table 'trafficlights'")
                return conn, cursor
            print("[WAIT] Table 'trafficlights' not found. Retrying...")
        except Error as e:
            print(f"[WAIT] MySQL not ready: {e}")
        time.sleep(5)
    raise Exception("❌ MySQL or table not available after multiple attempts")

mysql_conn, cursor = wait_for_mysql_and_table()

#Connect to Neo4j
print("[INIT] Connecting to Neo4j...")
graph = Graph(NEO4J_CONFIG["uri"], auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"]))

#Clear previous data

print("[INFO] Cleaning Neo4j database to resolve duplicate Status nodes...")
graph.run("MATCH (n) DETACH DELETE n")



#Create Status Nodes
status_values = ["red", "yellow", "green"]
status_nodes = {}
for status in status_values:
    node = Node("Status", name=status)
    graph.merge(node, "Status", "name")
    status_nodes[status] = node
print("[OK] Created/Merged Status nodes")

#Import Traffic Lights from MySQL
cursor.execute("SELECT * FROM trafficlights")
traffic_lights = cursor.fetchall()


for tl in traffic_lights:
    tl_node = Node(
        "TrafficLight",
        tl_id=tl["tl_id"],
        tl_name=tl["tl_name"],
        tl_intersection=tl["tl_intersection"],
        tl_productiondate=str(tl["tl_productiondate"])
    )

    graph.merge(tl_node, "TrafficLight", "tl_id")

    initial_status = random.choice(status_values)
    existing_status_node = graph.nodes.match("Status", name=initial_status).first()
    if existing_status_node:
        query = """
        MATCH (tl:TrafficLight {tl_id: $tl_id})
        MATCH (s:Status {name: $status_name})
        MERGE (tl)-[r:HAS_STATUS]->(s)
        SET r.timestamp = datetime()
        """
        graph.run(query, tl_id=tl["tl_id"], status_name=initial_status)
        print(f"[OK] Created/Merged initial HAS_STATUS relationship for TL ID {tl['tl_id']} to {initial_status}.")
    else:
        print(f"[WARN] Status node '{initial_status}' not found. Cannot link traffic light {tl['tl_id']}.")


print(f"[OK] Inserted/Merged {len(traffic_lights)} traffic lights and initial relationships into Neo4j")