from flask import Flask
from neo4j import GraphDatabase


# Function to initialize the Flask app and Neo4j connection
def create_app():
    app = Flask(__name__)

    # Establish connection to Neo4j
    neo4j_uri = 'neo4j+s://92c95011.databases.neo4j.io'
    neo4j_username = 'neo4j'
    neo4j_password = 'Q56E4WS-QJRjMJunYBLdcrd2UOR3JGPOLhZCyhMQW9c'

    if not neo4j_uri or not neo4j_username or not neo4j_password:
        raise ValueError("Neo4j connection details are not properly configured in the environment.")

    # Initialize Neo4j connection
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
    app.config['graph'] = driver

    with app.app_context():
        from app import models
        from app.routes import main, geolocate, graph_filter

        print("Registering blueprints...")
        
        app.register_blueprint(main.main_bp, url_prefix='/')
        print("Main routes registered.")
        
        app.register_blueprint(geolocate.geolocate_bp, url_prefix='/')
        print("Geolocate routes registered.")
        
        app.register_blueprint(graph_filter.filter_viz_bp, url_prefix='/')
        print("Graph filter routes registered.")


    return app