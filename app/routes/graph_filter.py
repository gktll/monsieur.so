from flask import  Blueprint, jsonify, request
from app.routes.constants import neo4j_driver

# Define the blueprint
filter_viz_bp = Blueprint('filter_viz', __name__)

driver = neo4j_driver

@filter_viz_bp.route('/api/filter_by_hour', methods=['POST'])
def filter_by_hour():
    data = request.json
    hour_name = data.get('hour_name')
    print(f"DEBUG: Received hour_name: {hour_name}")

    if not hour_name:
        return jsonify({"error": "Missing hour_name parameter"}), 400

    try:
        results = fetch_hour_data(hour_name, driver)
        filtered_nodes = []
        filtered_edges = []
        
        # Track nodes we've already added using their URIs
        added_node_uris = set()

        # Process each record
        for record in results:
            # Process primary connected node
            if record.get("connectedNode"):
                node_id = record["connectedNode"].get("uri")
                
                # Only add node if we haven't seen it before
                if node_id and node_id not in added_node_uris:
                    added_node_uris.add(node_id)
                    node_label = record["connectedNode"].get("hasName") or record["connectedNode"].get("label") or "Unnamed Node"
                    node_description = record["connectedNode"].get("description", "")
                    node_type = record.get("connectedNodeLabels", [])

                    filtered_nodes.append({
                        "id": node_id,
                        "label": node_label,
                        "description": node_description,
                        "type": node_type,
                    })

                # Add edge from hour to connected node
                filtered_edges.append({
                    "from": record["hour"]["uri"],
                    "to": node_id,
                    "label": record["hourRelationshipType"],
                    "properties": record.get("hourRelationshipProperties", {})
                })

                # Process planet node if it exists
                if record.get("planet"):
                    planet_id = record["planet"].get("uri")
                    
                    # Only add planet if we haven't seen it before
                    if planet_id and planet_id not in added_node_uris:
                        added_node_uris.add(planet_id)
                        planet_label = record["planet"].get("hasName") or record["planet"].get("label") or "Unnamed Planet"
                        planet_description = record["planet"].get("description", "")
                        planet_type = record.get("planetLabels", [])

                        filtered_nodes.append({
                            "id": planet_id,
                            "label": planet_label,
                            "description": planet_description,
                            "type": planet_type
                        })

                    # Add edge from connected node to planet
                    filtered_edges.append({
                        "from": node_id,
                        "to": planet_id,
                        "label": record["planetRelationshipType"],
                        "properties": record.get("planetRelationshipProperties", {})
                    })

        # Add hour node if not already added
        hour_node = next((record["hour"] for record in results if record["hour"]), None)
        if hour_node and hour_node["uri"] not in added_node_uris:
            filtered_nodes.append({
                "id": hour_node["uri"],
                "label": hour_node.get("hasName") or "Hour",
                "description": hour_node.get("description", ""),
                "type": ["Hour"]
            })

        return jsonify({
            "nodes": filtered_nodes,
            "edges": filtered_edges,
            "message": "Filtered data fetched successfully."
        })

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": f"Error fetching data: {str(e)}"}), 500
    


def fetch_hour_data(hour_name, driver):
    """
    Query Neo4j for the specific hour, its relationships, and related planet connections.
    """
    print(f"DEBUG: Fetching Neo4j data for hour_name: {hour_name}")
    with driver.session() as session:
        query = """
        MATCH (hour {uri: $hour_uri})
        OPTIONAL MATCH (hour)-[r1]-(connectedNode)
        OPTIONAL MATCH (connectedNode)-[r2]-(planet)
        WHERE 'PlanetEntity' IN labels(connectedNode)
        RETURN 
            hour { .uri, .hasName, .description, .hasSynonyms } AS hour,
            type(r1) AS hourRelationshipType,
            connectedNode { .* } AS connectedNode,
            properties(r1) AS hourRelationshipProperties,
            labels(connectedNode) AS connectedNodeLabels,
            planet { .* } AS planet,
            type(r2) AS planetRelationshipType,
            properties(r2) AS planetRelationshipProperties,
            labels(planet) AS planetLabels
        """
        print(f"DEBUG: Executing query:\n{query}\nWith parameter: {hour_name}")
        results = session.run(query, hour_uri=hour_name)  # Pass hour_name as hour_uri
        data = [record.data() for record in results]
        print(f"DEBUG: Raw query results:\n{data}")
        return data
