from py2neo import Graph, Node, Relationship
from datetime import datetime
import uuid

class Topic:
    def __init__(self, graph):
        self.graph = graph

    def create_topic(self, name, topic_type, subtype=None, description=None, image=None, notes=None):
        """
        Creates a new topic node in the Neo4j database or updates an existing one.
        """
        # Check if a topic with the same name and type already exists
        topic_node = self.graph.nodes.match("Topic", name=name, type=topic_type).first()
        
        if topic_node:
            # Update the existing node
            topic_node.update({
                "subtype": subtype,
                "description": description,
                "image": image,
                "notes": notes,
                "updated_at": datetime.now()
            })
            self.graph.push(topic_node)  # Save changes to the existing node
        else:
            # Create a new node if it doesn't exist
            topic_node = Node(
                "Topic",
                id=str(uuid.uuid4()),
                name=name,
                image=image,
                type=topic_type,
                subtype=subtype,
                notes=notes,
                descriptions=[description] if description else [],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.graph.create(topic_node)

        return topic_node



    # TOPIC DIRECT AND INFERRED ANALOGIES
    def add_direct_analogy(self, topic_id, analogous_topic_id, system_id):
        """
        Creates a bidirectional DIRECT_ANALOGY relationship between two topics with a system ID.
        Automatically creates the reverse analogy and updates inferred analogies.
        """
        topic_node = self.graph.nodes.match("Topic", id=topic_id).first()
        analogous_topic_node = self.graph.nodes.match("Topic", id=analogous_topic_id).first()
        
        if topic_node and analogous_topic_node:
            # Create the direct analogy relationship with the system_id property
            rel = Relationship(topic_node, "DIRECT_ANALOGY", analogous_topic_node, system_id=system_id)
            reverse_rel = Relationship(analogous_topic_node, "DIRECT_ANALOGY", topic_node, system_id=system_id)
            self.graph.create(rel)
            self.graph.create(reverse_rel)

            # Fetch all existing direct analogies for the analogous topic
            existing_analogies = self.get_direct_analogies(analogous_topic_id, system_id)

            # Add inferred analogies between the new topic and each existing analogous topic
            for existing_analogy in existing_analogies:
                if existing_analogy != topic_id:
                    self.add_inferred_analogy(topic_id, existing_analogy, system_id)
                    self.add_inferred_analogy(existing_analogy, topic_id, system_id)

    def get_direct_analogies(self, topic_id, system_id):
        """
        Retrieves all direct analogies for a specific topic in a specific system.
        """
        query = """
        MATCH (t:Topic {id: $topic_id})-[r:DIRECT_ANALOGY {system_id: $system_id}]->(related:Topic)
        RETURN related.id AS analogous_topic_id
        """
        results = self.graph.run(query, topic_id=topic_id, system_id=system_id)
        return [record["analogous_topic_id"] for record in results]
    

    def add_inferred_analogy(self, topic_id, inferred_topic_id, system_id):
        """
        Creates a one-way INFERRED_ANALOGY relationship between two topics with a system ID.
        """
        topic_node = self.graph.nodes.match("Topic", id=topic_id).first()
        inferred_topic_node = self.graph.nodes.match("Topic", id=inferred_topic_id).first()
        
        if topic_node and inferred_topic_node:
            # Create the inferred analogy relationship with the system_id property
            rel = Relationship(topic_node, "INFERRED_ANALOGY", inferred_topic_node, system_id=system_id)
            self.graph.create(rel)



     # DYNAMIC RELATIONSHIPS
    def add_dynamic_relationship(self, topic_id, related_topic_id, relationship_type, source_id=None):
        """
        Adds a dynamic relationship (like PRECEDES, FOLLOWS, etc.) between two topics with an optional source ID.
        """
        topic_node = self.graph.nodes.match("Topic", id=topic_id).first()
        related_topic_node = self.graph.nodes.match("Topic", id=related_topic_id).first()
        
        if topic_node and related_topic_node:
            if source_id:
                rel = Relationship(topic_node, relationship_type, related_topic_node, source_id=source_id)
            else:
                rel = Relationship(topic_node, relationship_type, related_topic_node)
            self.graph.create(rel)

    def update_dynamics(self, topic_id, **kwargs):
        """
        Adds dynamic relationships for an existing topic node based on the provided dynamic relationship fields.
        """
        dynamics = {
            "PRECEDES": kwargs.get("precedes"),
            "FOLLOWS": kwargs.get("follows"),
            "CATALYST_FOR": kwargs.get("catalyst_for"),
            "ANTAGONIST_OF": kwargs.get("antagonist_of"),
            "DERIVES_FROM": kwargs.get("derives_from"),
            "HAS_PROPERTY": kwargs.get("has_property"),
            "BINDS_TO": kwargs.get("binds_to"),
            "ENHANCES": kwargs.get("enhances"),
            "DECREASES": kwargs.get("decreases"),
            "EQUIVALENT_TO": kwargs.get("equivalent_to"),
            "SYNONYM_OF": kwargs.get("synonym_of"),
            "SIMILAR_TO": kwargs.get("similar_to"),
            "INFLUENCES": kwargs.get("influences"),
            "AFFILIATED_TO": kwargs.get("affiliated_to"),
            "IS_AUTHOR": kwargs.get("is_author"),
            "IS_PUBLISHER": kwargs.get("is_publisher"),
            "IS_BIBLIOGRAPHIC_SOURCE": kwargs.get("is_bibliographic_source")
        }

        for relationship, related_topic_id in dynamics.items():
            if related_topic_id:
                self.add_dynamic_relationship(topic_id, related_topic_id, relationship)


 
    # ANALOGY SYSTEMS
    def create_or_get_analogy_system(self, system_name, description=None):
        """
        Adds a new AnalogySystem node or retrieves an existing one based on its name.
        
        Parameters:
            - system_name: Name of the analogy system.
            - description: Optional description for the analogy system.
        """
        # Check if the system already exists
        system_node = self.graph.nodes.match("AnalogySystem", name=system_name).first()
        if not system_node:
            # Create a new system node if it doesn't exist
            system_node = Node("AnalogySystem", id=str(uuid.uuid4()), name=system_name, description=description)
            self.graph.create(system_node)
        return system_node





