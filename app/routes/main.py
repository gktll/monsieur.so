from flask import Blueprint, render_template, current_app, jsonify, request
from app.routes.constants import neo4j_driver
import json


main_bp = Blueprint('main_bp', __name__)

driver = neo4j_driver

# Fetch Network Graph from Neo4j
@main_bp.route('/api/graph_data')
def get_graph_data():
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    with driver.session() as session:
        results = session.run(query)
        nodes = {}
        edges = []

        for record in results:
            node1 = record["n"]
            node2 = record["m"]
            relationship = record["r"]

            for node in [node1, node2]:
                if node.id not in nodes:
                    label = node.get("label") or node.get("hasName") or node.get("uri")
                    nodes[node.id] = {
                        "id": node.id,
                        "label": label,
                        "title": json.dumps(dict(node.items()), indent=2),
                        "properties": dict(node.items()),
                    }

            edges.append({
                "from": node1.id,
                "to": node2.id,
                "label": relationship.type,
                "title": json.dumps(dict(relationship.items()), indent=2),
            })

    return jsonify({"nodes": list(nodes.values()), "edges": edges})



@main_bp.route('/api/heatmap', methods=['POST'])
def get_heatmap_data():
    """
    Generate heatmap data based on planetary positions.
    """
    try:
        # Parse request data
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is None or longitude is None:
            return jsonify({"error": "Missing latitude or longitude"}), 400

        # Import utilities
        from app.routes.utils.ephemeris_calculator import EphemerisCalculator
        from app.routes.utils.heatmap_calculator import HeatmapCalculator

        # Calculate ephemeris data
        ephemeris_data = EphemerisCalculator.calculate(latitude, longitude)

        # Extract hour ruler and day ruler from additional_info
        additional_info = ephemeris_data.get("additional_info", {})
        hour_ruler = additional_info.get("hour_ruler")
        day_ruling_planet = additional_info.get("day_ruling_planet")

        if not ephemeris_data or not ephemeris_data.get("planets"):
            return jsonify({"error": "Failed to calculate ephemeris data"}), 500

        # Log extracted rulers for debugging
        current_app.logger.debug(f"Hour Ruler: {hour_ruler}, Day Ruler: {day_ruling_planet}")

        # Generate heatmap data using HeatmapCalculator
        heatmap_data = HeatmapCalculator.calculate_heatmap_properties(
            ephemeris_data, hour_ruler, day_ruling_planet
        )

        # Return the heatmap data
        return jsonify({
            "heatmap": heatmap_data,
            "message": "Heatmap data generated successfully."
        })

    except Exception as e:
        current_app.logger.error(f"Heatmap error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500



# Landing page
@main_bp.route('/')
def landing_page():
    return render_template('landing_page.html')

# Admin Page Route
@main_bp.route('/admin')
def admin_page():
    return render_template('admin_page.html')

















# @main_bp.route('/topics', methods=['GET'])
# def list_topics():
#     """
#     Renders a page that lists all topics with options to edit or delete each topic.
#     """
#     graph = current_app.config['graph']

#     try:
#         # Retrieve all topic nodes from the database
#         query = "MATCH (t:Topic) RETURN t.id as id, t.name as name, t.type as type, t.subtype as subtype"
#         topics = graph.run(query).data()

#         return render_template('pages/topics_all.html', topics=topics), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



# @main_bp.route('/analogy_systems', methods=['GET'])
# def list_and_get_systems():
#     """
#     Handles both rendering the list of analogy systems for an HTML page and returning
#     systems in JSON format for dropdown population based on request type.
#     """
#     graph = current_app.config['graph']

#     try:
#         # Retrieve all system nodes from the database
#         query = "MATCH (s:AnalogySystem) RETURN s.id as id, s.name as name"
#         systems = graph.run(query).data()

#         if request.accept_mimetypes.best == 'application/json':
#             # If the request expects JSON, return JSON data (for the dropdown)
#             return jsonify(systems), 200

#         # Otherwise, render the systems page
#         return render_template('pages/analogy_systems_all.html', systems=systems), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
