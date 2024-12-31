from flask import Blueprint, jsonify
from app.routes.utils.ephemeris_calculator import EphemerisCalculator

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/ephemeris', methods=['GET'])
def test_ephemeris():
    # Example coordinates (New York City)
    latitude = 41.86676181022359
    longitude = 12.432721865311951

    # Initialize the EphemerisCalculator
    calculator = EphemerisCalculator(latitude=latitude, longitude=longitude)

    # Generate the dataset
    dataset = calculator.generate_ephemeris_dataset()

    # Return the dataset as a JSON response
    return jsonify(dataset)

