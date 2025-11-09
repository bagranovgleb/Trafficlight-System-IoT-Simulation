# app/db/neo4j_utils.py
from py2neo import Graph, Node, Relationship
from config import NEO4J_CONFIG
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

_graph = None

def get_graph():
    global _graph
    if _graph is None:
        for attempt in range(5):
            try:
                logger.info(f"Attempting to connect to Neo4j at {NEO4J_CONFIG['uri']} (Attempt {attempt + 1})...")
                _graph = Graph(NEO4J_CONFIG['uri'], auth=(NEO4J_CONFIG['user'], NEO4J_CONFIG['password']))
                _graph.run("RETURN 1") # test connection
                logger.info("Successfully connected to Neo4j.")
                return _graph
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)
        logger.error("Failed to connect to Neo4j after multiple attempts.")
        raise ConnectionError("Could not connect to Neo4j.")
    return _graph

# ---------- CREATION METHODS ----------
def create_traffic_light(tl_id, tl_name, intersection, production_date):
    graph = get_graph()
    tl_node = Node("TrafficLight",
                   tl_id=tl_id,
                   tl_name=tl_name,
                   tl_intersection=intersection,
                   production_date=str(production_date))
    graph.merge(tl_node, "TrafficLight", "tl_id")

def create_status_node(status_name):
    graph = get_graph()
    status_node = Node("Status", name=status_name.lower())
    graph.merge(status_node, "Status", "name")

def link_traffic_light_to_status(tl_id, status_name):
    graph = get_graph()
    graph.run("""
        MATCH (t:TrafficLight {tl_id: $tl_id}), (s:Status {name: $status})
        MERGE (t)-[r:HAS_STATUS]->(s)
        SET r.timestamp = datetime()
    """, parameters={"tl_id": tl_id, "status": status_name.lower()})


# ---------- QUERY FOR TRAFFIC LIGHT STATUS----------

def get_traffic_light_status():
    graph = get_graph()
    query = """
    MATCH (t:TrafficLight)
    OPTIONAL MATCH (t)-[r:HAS_STATUS]->(s:Status)
    RETURN t.tl_id AS tl_id,
           t.tl_name AS tl_name,
           t.tl_intersection AS intersection,
           s.name AS current_status,
           r.timestamp AS last_update
    ORDER BY tl_id
    """
    result = graph.run(query)
    return [record.data() for record in result]