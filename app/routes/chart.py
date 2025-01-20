# app/routes/chart.py
from flask import Blueprint, jsonify, request, current_app, render_template
from app.routes.utils.chart_calculator import ChartCalculator
from app.routes.ephemeris import get_ephemeris_data

chart_routes = Blueprint('chart_routes', __name__)
calculator = ChartCalculator()

chart_routes = Blueprint('chart_routes', __name__)
calculator = ChartCalculator()

@chart_routes.route('/api/chart-svg', methods=['POST'])
def generate_chart_svg():
    """Generate SVG chart using existing ephemeris data"""
    try:
        # Get data from the request
        data = request.get_json()
        
        # If we receive direct ephemeris data, use it
        if data and 'ephemeris' in data:
            ephemeris_data = data
        else:
            # Call ephemeris endpoint with the data from the request
            lat = data.get('latitude')
            lon = data.get('longitude')
            if lat is None or lon is None:
                return jsonify({"error": "Missing latitude or longitude"}), 400

            # Create a new request context with the required data
            with current_app.test_request_context('/api/ephemeris', 
                method='POST',
                json={'latitude': lat, 'longitude': lon}):
                    ephemeris_data = get_ephemeris_data()[0]  # Get just the response data
            
        # Generate SVG using the chart calculator
        svg = calculator.generate_chart_svg(ephemeris_data)
        
        return svg, 200, {'Content-Type': 'image/svg+xml'}
        
    except Exception as e:
        current_app.logger.error(f"Error generating chart: {str(e)}")
        return jsonify({"error": str(e)}), 500
      
      
      
@chart_routes.route('/chart')
def show_chart():
    return render_template('chart.html')