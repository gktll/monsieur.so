# routes.py
from flask import Flask, jsonify, request

from ephemeris_calculator import EphemerisCalculator
from heatmap_calculator import HeatmapCalculator
from neo4j_queries import Neo4jQueries

app = Flask(__name__)

@app.route('/api/ephemeris', methods=['POST'])
def ephemeris_data():
    data = request.json
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    calculator = EphemerisCalculator(latitude, longitude)
    ephemeris_dataset = calculator.generate_ephemeris_dataset()

    return jsonify(ephemeris_dataset)

@app.route('/api/heatmap', methods=['POST'])
def heatmap():
    data = request.json
    planetary_positions = data.get("planetary_positions")
    ruling_planet = data.get("ruling_planet")
    day_ruling_planet = data.get("day_ruling_planet")

    heatmap_data = HeatmapCalculator.calculate_heatmap_properties(
        planetary_positions, ruling_planet, day_ruling_planet
    )

    return jsonify(heatmap_data)
