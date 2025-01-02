from flask import Blueprint, jsonify 

from app.routes.utils.ephemeris_calculator import EphemerisCalculator
from app.routes.utils.neo4j_queries import Neo4jQueries

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/ephemeris', methods=['GET'])
def test_ephemeris():
    # Example coordinates (New York City)
    latitude = 41.86676181022359
    longitude = 12.432721865311951

    # Initialize the EphemerisCalculator
    calculator = EphemerisCalculator(latitude=latitude, longitude=longitude)
    dataset = calculator.generate_ephemeris_dataset()

    # Extract planetary positions from the dataset
    planetary_positions = dataset

    # Calculate the current planetary hour
    hour_index = calculator.calculate_planetary_hour()

    # Initialize Neo4jQueries
    neo4j = Neo4jQueries(calculator)

    # Fetch data for the current hour
    hour_name = neo4j.format_hour_name(hour_index)
    hour_data = neo4j.fetch_hour_data(hour_name, planetary_positions)

    return jsonify(hour_data)
