# app/routes/crud_routes.py
from flask import Blueprint, request, jsonify, render_template, current_app, json
from app.models import Topic  # Ensure you have imported Topic
from py2neo import Relationship

crud_bp = Blueprint('crud_bp', __name__)


#TOPICS
# CREATE FORM TO DISPLAY
@crud_bp.route('/add_topic', methods=['GET'])
def show_add_topic_form():
    return render_template('forms/topic_add.html')

# ADD TOPIC NODE
@crud_bp.route('/create_topic', methods=['POST'])
def create_topic():
    print("Create topic route accessed!") 
    # Fetch basic topic data
    name = request.form.get('name')
    image = request.form.get('image')
    topic_type = request.form.get('type')
    subtype = request.form.get('subtype')
    description = request.form.get('description')
    notes = request.form.get('notes')

    print(f"Name: {name}, Image: {image}, Type: {topic_type}, Subtype: {subtype}, Description: {description}, Notes: {notes}")

    if not name or not topic_type:
        return jsonify({"error": "Both name and type are required!"}), 400

    graph = current_app.config['graph']
    topic_model = Topic(graph)

    # Create or find an existing topic
    topic_node = topic_model.create_topic(
        name=name, 
        topic_type=topic_type, 
        subtype=subtype, 
        description=description, 
        image=image, 
        notes=notes
    )
    
    return jsonify({"message": f"Topic '{name}' created or updated!", "id": topic_node["id"]}), 201


@crud_bp.route('/delete_topic/<topic_id>', methods=['POST'])
def delete_topic(topic_id):
    """
    Deletes a topic and removes it from all analogies and dynamic relationships.
    """
    graph = current_app.config['graph']
    topic_model = Topic(graph)

    try:
        # Find the topic to be deleted
        topic_node = graph.nodes.match("Topic", id=topic_id).first()
        if not topic_node:
            return jsonify({"error": "Topic not found"}), 404

        # Delete all direct and inferred analogies related to the topic
        graph.run("""
            MATCH (t:Topic {id: $topic_id})-[r:IS_ANALOGOUS_TO]-(related:Topic)
            DELETE r
        """, topic_id=topic_id)

        # Delete all dynamic relationships involving the topic
        graph.run("""
            MATCH (t:Topic {id: $topic_id})-[r]->() 
            DELETE r
        """, topic_id=topic_id)

        # Delete the topic node itself
        graph.run("MATCH (t:Topic {id: $topic_id}) DELETE t", topic_id=topic_id)

        return jsonify({"message": f"Topic '{topic_id}' and its related relationships have been deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ANALOGIES
@crud_bp.route('/add_analogies', methods=['POST'])
def add_analogies():
    topic_id = request.form.get('topic_id')
    analogies = request.form.getlist('analogies')
    system_id = request.form.get('system_id')

    if not topic_id or not analogies or not system_id:
        return jsonify({"error": "Topic ID, Analogies, and System ID are required!"}), 400

    graph = current_app.config['graph']
    topic_model = Topic(graph)

    try:
        for related_topic in analogies:
            topic_model.add_direct_analogy(topic_id, related_topic, system_id)
        
        return jsonify({"message": f"Analogies added to topic '{topic_id}'."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@crud_bp.route('/process_analogies', methods=['POST'])
def process_analogies():
    try:
        topic_id = request.form.get('topic_id')
        analogy_data = request.form.get('selected_analogies')  # JSON data with analogy systems and related topics
        
        if not topic_id or not analogy_data:
            return jsonify({"error": "Topic ID and analogy data are required!"}), 400

        analogy_list = json.loads(analogy_data)
        print("Analogy Data:", analogy_list)  # Debug log

        graph = current_app.config['graph']
        topic_model = Topic(graph)

        for analogy_system in analogy_list:
            system_id = analogy_system.get('system_id')
            topics = analogy_system.get('topics', [])

            for related_topic in topics:
                related_topic_id = related_topic.get('id')
                
                # Add direct analogy relationships
                topic_model.add_direct_analogy(topic_id, related_topic_id, system_id)
        
        return jsonify({"message": "Analogies processed successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# DYNNAMIC RELATIONHSIPS
def add_dynamic_relationship(self, topic_id, related_topic_id, relationship_type, source):
    """
    Adds or updates a dynamic relationship between two topics, including source and frequency.
    """
    # Match the two nodes
    topic_node = self.graph.nodes.match("Topic", id=topic_id).first()
    related_topic_node = self.graph.nodes.match("Topic", id=related_topic_id).first()
    
    if topic_node and related_topic_node:
        # Check if the relationship already exists
        existing_relationship = self.graph.match((topic_node, related_topic_node), r_type=relationship_type).first()
        
        if existing_relationship:
            # Update the existing relationship by incrementing frequency and adding a new source
            sources = existing_relationship.get("sources", [])
            if source not in sources:
                sources.append(source)
            frequency = existing_relationship.get("frequency", 0) + 1

            existing_relationship["sources"] = sources
            existing_relationship["frequency"] = frequency
            self.graph.push(existing_relationship)
        else:
            # Create a new relationship with the source and initial frequency of 1
            new_relationship = Relationship(topic_node, relationship_type, related_topic_node,
                                            sources=[source], frequency=1)
            self.graph.create(new_relationship)
    





# SYSTEMS

# Route to show the form to add an analogy system
@crud_bp.route('/add_analogy_system', methods=['GET'])
def show_add_analogy_system_form():
    return render_template('forms/analogy_system_add.html')


# Route to create an analogy system
@crud_bp.route('/create_analogy_system', methods=['POST'])
def create_analogy_system():
    system_name = request.form.get('system_name')
    description = request.form.get('description')  # Fetch the description

    if not system_name:
        return jsonify({"error": "System name is required!"}), 400

    graph = current_app.config['graph']
    topic_model = Topic(graph)

    try:
        # Add or retrieve the analogy system node
        topic_model.create_or_get_analogy_system(system_name, description)
        return jsonify({"message": f"Analogy system '{system_name}' added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to show the form to edit an analogy system
@crud_bp.route('/edit_analogy_system/<system_id>', methods=['GET'])
def show_edit_analogy_system_form(system_id):
    """
    Renders the form to edit an existing analogy system.
    """
    graph = current_app.config['graph']
    try:
        # Retrieve the analogy system node using the graph directly
        analogy_system = graph.nodes.match("AnalogySystem", id=system_id).first()
        if not analogy_system:
            return jsonify({"error": "Analogy system not found"}), 404

        return render_template('forms/analogy_system_edit.html', analogy_system=analogy_system), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete an existing analogy system
@crud_bp.route('/delete_analogy_system/<system_id>', methods=['POST'])
def delete_analogy_system(system_id):
    """
    Deletes an analogy system by its ID.
    """
    graph = current_app.config['graph']

    try:
        # Find and delete the analogy system
        analogy_system = graph.nodes.match("AnalogySystem", id=system_id).first()
        if not analogy_system:
            return jsonify({"error": "Analogy system not found"}), 404

        graph.delete(analogy_system)
        return jsonify({"message": f"Analogy system '{system_id}' deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
