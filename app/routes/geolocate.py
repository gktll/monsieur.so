from flask import Blueprint, jsonify, request

from app.routes.utils.ephemeris_calculator import EphemerisCalculator
from app.routes.utils.neo4j_queries import Neo4jQueries
from app.routes.utils.heatmap_calculator import HeatmapCalculator
from app.routes.ephemeris import get_ephemeris_data

geolocate_bp = Blueprint('geolocate', __name__)

@geolocate_bp.route('/api/geolocation_ephemeris', methods=['POST'])
def handle_geolocation_and_visualization():
    """Handles the complete view with ephemeris, Neo4j data, and visualization."""
    try:
        data = request.json
        
        # Get ephemeris data directly from the function
        ephemeris_response = get_ephemeris_data()
        if ephemeris_response.status_code != 200:
            return ephemeris_response
            
        dataset = ephemeris_response.json['ephemeris']
        
        # Calculate Neo4j data
        calculator = EphemerisCalculator(
            latitude=data['latitude'], 
            longitude=data['longitude']
        )
        hour_index = calculator.calculate_planetary_hour()
        neo4j = Neo4jQueries(calculator)
        hour_name = neo4j.format_hour_name(hour_index)
        neo4j_data = neo4j.fetch_hour_data(hour_name, dataset)

        if neo4j_data.get("hour_ruler"):
            dataset["additional_info"]["hour_ruler"] = neo4j_data["hour_ruler"]

        
        # Calculate visualization data
        heatmap_data = HeatmapCalculator.calculate_heatmap_properties(
            ephemeris_data=dataset,
            hour_ruler=dataset["additional_info"].get("hour_ruler"),
            day_ruling_planet=dataset.get('additional_info', {}).get('day_ruling_planet'),
        )

        return jsonify({
            "latitude": data['latitude'],
            "longitude": data['longitude'],
            "ephemeris": dataset,
            "neo4j_data": neo4j_data,
            "heatmap_data": heatmap_data,
            "message": "View data generated successfully"
        })

    except Exception as e:
        print("DEBUG: Error occurred in visualization generation:", str(e))
        return jsonify({"error": str(e)}), 500