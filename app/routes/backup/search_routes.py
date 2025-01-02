from flask import Blueprint, request, jsonify, current_app

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/search_topics', methods=['GET'])
def search_topics():
    """
    Searches topics based on a query string for use in analogy autocomplete.
    """
    query = request.args.get('q', '').strip()  # Get the search query from the URL parameter

    if not query:
        return jsonify({"error": "Query parameter is required!"}), 400

    graph = current_app.config['graph']

    try:
        # Search for topics by name (adjust query to include other fields if necessary)
        result = graph.run("""
            MATCH (t:Topic)
            WHERE toLower(t.name) CONTAINS toLower($query)
            RETURN t.id as id, t.name as name, t.type as type, t.subtype as subtype
            LIMIT 20
        """, query=query).data()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add more search or filtering routes as needed
