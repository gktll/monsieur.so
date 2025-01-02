from flask import Blueprint, jsonify, request

from app.routes.utils.ephemeris_calculator import EphemerisCalculator
from app.routes.utils.neo4j_queries import Neo4jQueries
from app.routes.utils.heatmap_calculator import HeatmapCalculator

geolocate_bp = Blueprint('geolocate', __name__)

@geolocate_bp.route('/api/geolocation_ephemeris', methods=['POST'])
def handle_geolocation_and_ephemeris():
    """Handle geolocation data and calculate ephemeris."""
    try:
        data = request.json
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({"error": "Missing latitude or longitude"}), 400

        # Initialize EphemerisCalculator
        calculator = EphemerisCalculator(latitude=latitude, longitude=longitude)
        dataset = calculator.generate_ephemeris_dataset()
        # print(f"DEBUG: Generated Dataset: {dataset}")

        # Calculate planetary hour and hour name
        hour_index = calculator.calculate_planetary_hour()
        neo4j = Neo4jQueries(calculator)
        hour_name = neo4j.format_hour_name(hour_index)

        # Fetch Neo4j data
        neo4j_data = neo4j.fetch_hour_data(hour_name, dataset)
        
        if neo4j_data.get("hour_ruler"):
            dataset["additional_info"]["hour_ruler"] = neo4j_data["hour_ruler"]

        # Pass only hour_ruler and day_ruling_planet to HeatmapCalculator
        heatmap_data = HeatmapCalculator.calculate_heatmap_properties(
            ephemeris_data=dataset,  # Pass the full dataset
            hour_ruler=dataset["additional_info"].get("hour_ruler"),
            day_ruling_planet=dataset.get('additional_info', {}).get('day_ruling_planet'),
        )

        # Prepare response
        response_data = {
            "latitude": latitude,
            "longitude": longitude,
            "ephemeris": dataset,
            "neo4j_data": neo4j_data,
            "heatmap_data": heatmap_data,
            "message": "Calculations completed successfully"
        }
        print("DEBUG: Final response data:", response_data)
        return jsonify(response_data)

    except Exception as e:
      print("DEBUG: Error occurred:", str(e))
      return jsonify({"error": str(e)}), 500
