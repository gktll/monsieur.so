from flask import Blueprint, jsonify, request
from app.routes.utils.neo4j_queries import Neo4jQueries

filter_viz_bp = Blueprint('filter_viz', __name__)

@filter_viz_bp.route('/api/filter_by_hour', methods=['POST'])
def filter_by_hour():
    data = request.json
    hour_name = data.get('hour_name')

    if not hour_name:
        return jsonify({"error": "Missing hour_name parameter"}), 400

    try:
        neo4j = Neo4jQueries()
        results = neo4j.fetch_hour_graph(hour_name)

        filtered_nodes = []
        filtered_edges = []
        added_node_uris = set()

        for record in results:
            if record.get("connectedNode"):
                node_id = record["connectedNode"].get("uri")
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

                filtered_edges.append({
                    "from": record["hour"]["uri"],
                    "to": node_id,
                    "label": record["hourRelationshipType"],
                    "properties": record.get("hourRelationshipProperties", {})
                })

                if record.get("planet"):
                    planet_id = record["planet"].get("uri")
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

                    filtered_edges.append({
                        "from": node_id,
                        "to": planet_id,
                        "label": record["planetRelationshipType"],
                        "properties": record.get("planetRelationshipProperties", {})
                    })

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
        return jsonify({"error": str(e)}), 500





# THIS IS SUPPOSED TO GENERALIZE FILTERING

# @filter_viz_bp.route('/api/filter_graph', methods=['POST'])
# def filter_graph():
#     """
#     Generic graph filter that can handle multiple filter types.
    
#     Expected request format:
#     {
#         "filter_type": "planet|sign|element|quality|etc",
#         "filter_value": "Mars|Aries|Fire|Cardinal|etc",
#         "include_relationships": ["RULES", "INFLUENCES", "IN_SIGN", etc]  # optional
#     }
#     """
#     try:
#         data = request.json
#         filter_type = data.get('filter_type')
#         filter_value = data.get('filter_value')
#         relationships = data.get('include_relationships', [])

#         if not filter_type or not filter_value:
#             return jsonify({"error": "Missing filter parameters"}), 400

#         neo4j = Neo4jQueries()
#         results = neo4j.fetch_filtered_graph(filter_type, filter_value, relationships)

#         filtered_nodes = []
#         filtered_edges = []
#         added_node_uris = set()

#         # Process results and build graph
#         for record in results:
#             # Add nodes and edges based on filter type
#             process_node_and_relationships(
#                 record, 
#                 filtered_nodes, 
#                 filtered_edges, 
#                 added_node_uris
#             )

#         return jsonify({
#             "nodes": filtered_nodes,
#             "edges": filtered_edges,
#             "filter_applied": {
#                 "type": filter_type,
#                 "value": filter_value
#             },
#             "message": "Graph filtered successfully"
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
    
    
# def process_node_and_relationships(record, nodes, edges, added_uris):
#     """Process nodes and edges based on record type"""
#     if record.get("node"):
#         add_node_if_new(record["node"], nodes, added_uris)
        
#         # Add connected nodes and their relationships
#         for rel in record.get("relationships", []):
#             target_node = rel.get("node")
#             if target_node:
#                 add_node_if_new(target_node, nodes, added_uris)
#                 edges.append({
#                     "from": record["node"]["uri"],
#                     "to": target_node["uri"],
#                     "label": rel["type"],
#                     "properties": rel.get("properties", {})
#                 })

# def add_node_if_new(node, nodes_list, added_uris):
#     """Add node to list if not already present"""
#     if node["uri"] not in added_uris:
#         added_uris.add(node["uri"])
#         nodes_list.append({
#             "id": node["uri"],
#             "label": node.get("hasName") or node.get("label", "Unnamed"),
#             "description": node.get("description", ""),
#             "type": node.get("labels", [])
#         })