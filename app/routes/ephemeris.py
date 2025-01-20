# app/routes/ephemeris.py

from flask import Blueprint, jsonify, request
from app.routes.utils.ephemeris_calculator import EphemerisCalculator

ephemeris_bp = Blueprint('ephemeris', __name__)

@ephemeris_bp.route('/api/ephemeris', methods=['POST'])
def get_ephemeris_data():
    """Base endpoint that provides pure ephemeris calculations."""
    try:
        data = request.json
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is None or longitude is None:
            return jsonify({"error": "Missing latitude or longitude"}), 400

        calculator = EphemerisCalculator(latitude=latitude, longitude=longitude)
        dataset = calculator.generate_ephemeris_dataset()

        return jsonify({
            "ephemeris": dataset,
            "message": "Ephemeris data generated successfully"
        })

    except Exception as e:
        print("DEBUG: Error occurred in ephemeris calculation:", str(e))
        return jsonify({"error": str(e)}), 500