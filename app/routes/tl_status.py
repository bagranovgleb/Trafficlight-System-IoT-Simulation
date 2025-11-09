from flask import Blueprint, render_template
from db.neo4j_utils import get_traffic_light_status
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


traffic_light_status_bp = Blueprint('traffic_light_status_bp', __name__)


@traffic_light_status_bp.route("/traffic-light-status")
@traffic_light_status_bp.route("/")
def traffic_light_status():
    logger.info("Attempting to fetch traffic light status from Neo4j...")
    try:
        lights = get_traffic_light_status()
        logger.info(f"Successfully fetched {len(lights)} traffic lights from Neo4j.")
        logger.debug(f"Fetched lights data: {lights}")
    except Exception as e:
        lights = [] 
        logger.error(f"Error fetching traffic light status from Neo4j: {e}")

    # For debugging prints what's being passed
    print(f"[DEBUG] Data passed to template (lights): {lights}")

    return render_template("traffic_light_status.html", lights=lights)