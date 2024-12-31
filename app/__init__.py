from flask import Flask
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Fetch Neo4j credentials from environment variables
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Ensure Neo4j credentials are loaded
    if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
        raise ValueError("Neo4j connection details are missing in the environment variables.")

    # Initialize Neo4j driver
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD),
        connection_timeout=120
    )

    # Test the connection
    try:
        driver.verify_connectivity()
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Neo4j: {e}")

    app.config['graph'] = driver
    

    with app.app_context():
        from app import models
        from app.routes import main, geolocate, graph_filter
        from app.routes.test_ephemeris import test_bp

        print("Registering blueprints...")
        
        app.register_blueprint(main.main_bp, url_prefix='/')
        print("Main routes registered.")
        
        app.register_blueprint(geolocate.geolocate_bp, url_prefix='/')
        print("Geolocate routes registered.")
        
        app.register_blueprint(graph_filter.filter_viz_bp, url_prefix='/')
        print("Graph filter routes registered.")
        
        app.register_blueprint(test_bp, url_prefix='/')
        print("Test Ephemeris routes registered.")


    return app