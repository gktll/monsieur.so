# ------------------------------------
## UPLOAD SUPERCLASS
# ------------------------------------

# import yaml
# import json  # Import for serialization
# from neo4j import GraphDatabase

# # Initialize the Neo4j driver
# uri = "neo4j+s://eb32f100.databases.neo4j.io"
# user = "neo4j"
# password = "DGXWFgCX7QiAMLk-6ZSJs7ZZwGN7PM1Ps7F6Jh6-eGw"
# driver = GraphDatabase.driver(uri, auth=(user, password))

# # Create constraints for unique URIs
# def create_constraints():
#     with driver.session() as session:
#         session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.uri IS UNIQUE;")

# def flatten_properties(properties):
#     flat_properties = {}
#     for key, value in properties.items():
#         if isinstance(value, dict) and "default" in value:
#             flat_properties[key] = value.get("default", "")
#         else:
#             flat_properties[key] = value  # Keep primitive values directly
#     print(f"Flattened properties: {flat_properties}")  # Debug output
#     return flat_properties

# def serialize_properties(properties):
#     serialized_properties = {}
#     for key, value in properties.items():
#         if isinstance(value, dict) or isinstance(value, list):  # Complex types
#             serialized_properties[key] = json.dumps(value)
#         else:  # Primitive types
#             serialized_properties[key] = value
#     print(f"Serialized properties: {serialized_properties}")  # Debug output
#     return serialized_properties


# # Create the superclass node
# def create_superclass(tx, label, uri, properties):
#     query = """
#     MERGE (n:Entity { uri: $uri })
#     SET n += $properties
#     RETURN n
#     """
#     tx.run(query, uri=uri, properties=properties)

# # Upload superclass data from YAML
# def upload_superclass_from_yaml(yaml_file):
#     with open(yaml_file, "r") as file:
#         data = yaml.safe_load(file)

#     # Extract the Entity superclass details
#     superclass = data.get("classes", {}).get("Entity", {})
#     uri = superclass.get("uri")
#     label = superclass.get("label", "Entity")

#     # Flatten properties
#     default_properties = flatten_properties(superclass.get("defaultProperties", {}))
#     analogy_properties = flatten_properties(superclass.get("analogyProperties", {}))
#     discovered_relationships = flatten_properties(superclass.get("discoveredRelationships", {}))

#     # Serialize properties to JSON where needed
#     properties = serialize_properties({
#         "label": label,
#         "description": superclass.get("description", ""),
#         **default_properties,
#         **analogy_properties,
#         **discovered_relationships,
#     })

#     with driver.session() as session:
#         # Step 1: Create constraints
#         create_constraints()

#         # Step 2: Create Entity superclass node
#         session.execute_write(create_superclass, label, uri, properties)

# # Specify the path to your YAML file
# yaml_file_path = "/Users/fede/Desktop/git/monsieur_neo/ontologies/_superclassEntity.yaml"
# upload_superclass_from_yaml(yaml_file_path)




#  ------------------------------------
# UPLOAD CLASSES SUBCCLASSES AND INSTANCES
# ------------------------------------

import yaml
from neo4j import GraphDatabase

# Initialize the Neo4j driver
uri = "neo4j+s://eb32f100.databases.neo4j.io"
user = "neo4j"
password = "DGXWFgCX7QiAMLk-6ZSJs7ZZwGN7PM1Ps7F6Jh6-eGw"
driver = GraphDatabase.driver(uri, auth=(user, password))

# Create constraints for unique URIs
def create_constraints():
    with driver.session() as session:
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:SpiritualEntity) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Angel) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Demon) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Elemental) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:Intelligence) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:WeekDayEntity) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:PlanetEntity) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:ChemicalSubstanceEntity) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:MetalEntity) REQUIRE n.uri IS UNIQUE;")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (n:MagicHourEntity) REQUIRE n.uri IS UNIQUE;")


# Create nodes with properties
def create_node(tx, label, uri, properties):
    label = label.replace(" ", "").split(":")[-1]  # Normalize the label
    if not label:
        raise ValueError("Node label cannot be empty.")

    query = f"""
    MERGE (n:{label} {{ uri: $uri }})
    SET n += $properties
    RETURN n
    """
    tx.run(query, uri=uri, properties=properties)



# Create subclass relationships
def create_subclass_relationship(tx, child_label, child_uri, parent_label, parent_uri):
    query = f"""
    MATCH (parent:{parent_label} {{ uri: $parent_uri }}), (child:{child_label} {{ uri: $child_uri }})
    MERGE (child)-[:SUBCLASS_OF]->(parent)
    """
    tx.run(query, child_uri=child_uri, parent_uri=parent_uri)



# Create instance relationships (e.g., HAS_MEMBER)
def create_instance_relationship(tx, instance_label, instance_uri, parent_label, parent_uri):
    instance_label = instance_label.replace(" ", "").split(":")[-1]
    parent_label = parent_label.replace(" ", "").split(":")[-1]
    query = f"""
    MATCH (parent:{parent_label} {{ uri: $parent_uri }}), (instance:{instance_label} {{ uri: $instance_uri }})
    MERGE (instance)-[:HAS_MEMBER]->(parent)
    """
    tx.run(query, instance_uri=instance_uri, parent_uri=parent_uri)



def flatten_properties(properties):
    """
    Flatten complex property definitions into a dictionary of key-value pairs.
    Extract the `default` value or ensure lists are returned properly.
    """
    flat_properties = {}
    for key, value in properties.items():
        if isinstance(value, dict):
            # Extract the `default` value if available
            flat_value = value.get("default", None)
            if isinstance(flat_value, list):
                flat_properties[key] = flat_value  # Keep list as is
            elif flat_value is None:  # Default to empty list for list properties
                flat_properties[key] = []
            else:
                flat_properties[key] = flat_value  # Primitive value
        elif isinstance(value, list):
            # Handle unexpected nested lists directly
            flat_properties[key] = [item if isinstance(item, (str, int, float, bool)) else str(item) for item in value]
        else:
            flat_properties[key] = value  # Keep primitive values directly
    return flat_properties


def validate_properties(properties):
    """
    Ensure all property values are either primitive types or arrays of primitives.
    Replace `None` with appropriate defaults.
    """
    for key, value in properties.items():
        if value is None:  # Replace None with an appropriate default
            if isinstance(value, list):
                properties[key] = []  # Empty list for list properties
            else:
                properties[key] = ""  # Empty string for string properties
        elif isinstance(value, list):  # Ensure list contains only primitive types
            if not all(isinstance(item, (str, int, float, bool)) for item in value):
                raise ValueError(f"Invalid list elements for {key}: {value}")
        elif not isinstance(value, (str, int, float, bool, list)):  # Invalid type
            raise ValueError(f"Invalid property value for {key}: {value}")
    return properties




def upload_instance(tx, instance_name, instance_data, default_properties, classes):
    """
    Upload an instance, inheriting properties only from its immediate parent (class or subclass).
    """
    # Extract instance-specific data
    label = instance_data.get("label", "").strip()
    uri = instance_data.get("uri", "").strip()
    parent_label = instance_data.get("relationships", [{}])[0].get("HAS_MEMBER")

    if not label or not uri:
        raise ValueError(f"Missing label or URI for instance: {instance_name}, data: {instance_data}")

    # Identify the parent class or subclass
    parent_class_data = classes.get(parent_label, {})
    parent_uri = parent_class_data.get("uri")
    if not parent_uri:
        raise ValueError(f"Missing parent URI for instance: {instance_name}, parent_label: {parent_label}")

    # Merge properties, prioritizing instance-specific properties
    properties = {
        **default_properties,  # Default properties from superclass
        **parent_class_data.get("classProperties", {}),  # Class-level properties
        **parent_class_data.get("subclassProperties", {}),  # Subclass-level properties
        **instance_data.get("defaultProperties", {}),  # Instance-specific default properties
        **instance_data.get("classProperties", {}),  # Instance-specific class properties
        **instance_data.get("subclassProperties", {}),  # Instance-specific subclass properties
        "description": instance_data.get("description", ""),  # Add instance-specific description
    }

    # Debugging information
    print(f"Merged properties for instance '{instance_name}': {properties}")

    # Validate properties before uploading
    properties = validate_properties(properties)

    # Create the instance node
    create_node(tx, label, uri, properties)

    # Create the instance-to-class relationship
    if parent_label and parent_uri:
        create_instance_relationship(tx, label, uri, parent_label, parent_uri)


def upload_from_yaml(yaml_file):
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)

    with driver.session() as session:
        classes = data.get("classes", {})
        superclass = classes.get("Entity", {})
        default_properties = flatten_properties(superclass.get("defaultProperties", {}))

        # Step 1: Create constraints
        create_constraints()

        # Step 2: Create class nodes and SUBCLASS_OF relationships
        for class_name, class_data in classes.items():
            label = class_data.get("label", class_name).replace(" ", "").split(":")[-1]
            uri = class_data.get("uri")
            analogy_properties = flatten_properties(class_data.get("analogyProperties", {}))  # Flatten analogy properties

            properties = {
                "label": label,
                "description": class_data.get("description", ""),
                **flatten_properties(class_data.get("subclassProperties", {})),
                **analogy_properties,  # Add analogy properties to class-level properties
            }

            session.write_transaction(create_node, label, uri, properties)

            parent_label = class_data.get("subClassOf")
            if parent_label:
                parent_uri = classes.get(parent_label, {}).get("uri")
                if parent_uri:
                    session.write_transaction(
                        create_subclass_relationship,
                        label,
                        uri,
                        parent_label,
                        parent_uri
                    )

        # Step 3: Create instance nodes and HAS_MEMBER relationships
        instances = data.get("instances", {})
        for instance_name, instance_data in instances.items():
            session.write_transaction(
                upload_instance,
                instance_name,
                instance_data,
                default_properties,
                classes
            )

# Specify the path to your YAML file
yaml_file_path = "/Users/fede/Desktop/git/monsieur_neo/ontologies/colorEntity.yaml"
upload_from_yaml(yaml_file_path)


# ------------------------------------
# UPLOAD ANALOGIES
# ------------------------------------

# ------------------------------------
# !! this returns all nodes within a given system using traversal query
# MATCH path = (start)-[:HAS_ANALOGY_WITH*1..2]-(end)
# WHERE start.hasName = "Gold_0"
#   AND all(r IN relationships(path) WHERE r.system = "monsieur:AnalogySystemEntity/KeyOfSolomon")
# RETURN path
# ------------------------------------

# import yaml
# from neo4j import GraphDatabase

# # Initialize Neo4j driver
# uri = "neo4j+s://eb32f100.databases.neo4j.io"
# user = "neo4j"
# password = "DGXWFgCX7QiAMLk-6ZSJs7ZZwGN7PM1Ps7F6Jh6-eGw"
# driver = GraphDatabase.driver(uri, auth=(user, password))


# def upload_data_from_yaml(yaml_file):
#     """
#     Parse analogies and discovered relationships from YAML and upload to Neo4j.
#     """
#     with open(yaml_file, "r") as file:
#         data = yaml.safe_load(file)

#     instances = data.get("instances", {})
#     analogy_data = []
#     discovered_relationships_data = []

#     # Extract analogy and discovered relationship properties
#     for instance_name, instance_data in instances.items():
#         source_uri = instance_data.get("uri")

#         # Process analogy properties
#         analogy_properties = instance_data.get("analogyProperties", {}).get("hasAnalogyWith", [])
#         for analogy in analogy_properties:
#             target_entity = analogy.get("targetEntity", {})
#             analogy_system = analogy.get("analogySystem", {})
#             confidence = analogy.get("confidence", {})

#             analogy_data.append({
#                 "source": {"uri": source_uri},
#                 "target": target_entity,
#                 "system": analogy_system,
#                 "confidence": confidence
#             })

#         # Process discovered relationships
#         discovered_relationships = instance_data.get("discoveredRelationships", {}).get("hasRelationshipWith", [])
#         for relationship in discovered_relationships:
#             target_entity = relationship.get("relatedEntity", {})
#             relationship_type = relationship.get("relationshipType", "RELATIONSHIP")
#             source = relationship.get("source", {})

#             discovered_relationships_data.append({
#                 "source": {"uri": source_uri},
#                 "target": target_entity,
#                 "type": relationship_type,
#                 "source_details": source
#             })

#     # Upload data to Neo4j
#     upload_analogies(analogy_data)
#     upload_discovered_relationships(discovered_relationships_data)


# def upload_analogies(analogies):
#     """
#     Upload analogies to Neo4j.
#     """
#     with driver.session() as session:
#         for analogy in analogies:
#             source_uri = analogy['source']['uri']
#             target_uri = analogy['target']['uri']
#             analogy_system = analogy['system']
#             confidence = analogy.get('confidence', {})
#             source_id = confidence.get('source_id', "")
#             quote_id = confidence.get('quote_id', "")
#             feed = confidence.get('feed', "manual")
#             score = confidence.get('score', 1.0)

#             session.write_transaction(
#                 create_analogy_relationship,
#                 source_uri,
#                 target_uri,
#                 analogy_system,
#                 score,
#                 source_id,
#                 quote_id,
#                 feed
#             )


# def create_analogy_relationship(tx, source_uri, target_uri, analogy_system, score, source_id, quote_id, feed):
#     """
#     Create a bidirectional analogy relationship between two nodes.
#     """
#     query = """
#     MATCH (source {uri: $source_uri}), (target {uri: $target_uri})
#     MERGE (source)-[r:HAS_ANALOGY_WITH {system: $analogy_system}]->(target)
#     SET r += {
#         confidence_score: $score,
#         source_id: $source_id,
#         quote_id: $quote_id,
#         feed: $feed
#     }
#     MERGE (target)-[reverse:HAS_ANALOGY_WITH {system: $analogy_system}]->(source)
#     SET reverse += {
#         confidence_score: $score,
#         source_id: $source_id,
#         quote_id: $quote_id,
#         feed: $feed
#     }
#     """
#     tx.run(
#         query,
#         source_uri=source_uri,
#         target_uri=target_uri,
#         analogy_system=analogy_system['uri'],
#         score=score,
#         source_id=source_id,
#         quote_id=quote_id,
#         feed=feed
#     )


# def upload_discovered_relationships(relationships):
#     """
#     Upload discovered relationships to Neo4j.
#     """
#     with driver.session() as session:
#         for relationship in relationships:
#             source_uri = relationship['source']['uri']
#             target_uri = relationship['target']['uri']
#             relationship_type = relationship['type']
#             source_details = relationship.get('source_details', {})
#             source_id = source_details.get('source_id', "")
#             quote_id = source_details.get('quote_id', "")
#             confidence_score = source_details.get('confidence_score', 1.0)
#             feed = source_details.get('feed', "manual")

#             session.write_transaction(
#                 create_discovered_relationship,
#                 source_uri,
#                 target_uri,
#                 relationship_type,
#                 confidence_score,
#                 source_id,
#                 quote_id,
#                 feed
#             )


# def create_discovered_relationship(tx, source_uri, target_uri, relationship_type, confidence_score, source_id, quote_id, feed):
#     """
#     Create a unidirectional discovered relationship between two nodes.
#     """
#     query = f"""
#     MATCH (source {{uri: $source_uri}}), (target {{uri: $target_uri}})
#     MERGE (source)-[r:{relationship_type}]->(target)
#     SET r += {{
#         confidence_score: $confidence_score,
#         source_id: $source_id,
#         quote_id: $quote_id,
#         feed: $feed
#     }}
#     """
#     tx.run(
#         query,
#         source_uri=source_uri,
#         target_uri=target_uri,
#         confidence_score=confidence_score,
#         source_id=source_id,
#         quote_id=quote_id,
#         feed=feed
#     )


# # Example usage
# yaml_file_path = "/Users/fede/Desktop/git/monsieur_neo/ontologies/magicHourEntity.yaml"
# upload_data_from_yaml(yaml_file_path)



# ------------------------------------
# UPLOAD MAGIC HOURS RELATIONSHIPS
# ------------------------------------
# import yaml
# from neo4j import GraphDatabase

# # Initialize Neo4j driver
# uri = "neo4j+s://eb32f100.databases.neo4j.io"
# user = "neo4j"
# password = "DGXWFgCX7QiAMLk-6ZSJs7ZZwGN7PM1Ps7F6Jh6-eGw"
# driver = GraphDatabase.driver(uri, auth=(user, password))


# def log_message(message, level="INFO"):
#     """
#     Log messages to the terminal.
#     """
#     levels = {
#         "INFO": "\033[94m[INFO]\033[0m",
#         "WARNING": "\033[93m[WARNING]\033[0m",
#         "ERROR": "\033[91m[ERROR]\033[0m"
#     }
#     print(f"{levels.get(level, '[LOG]')} {message}")


# def upload_data_from_yaml(yaml_file):
#     """
#     Parse discovered relationships from YAML and upload to Neo4j.
#     """
#     with open(yaml_file, "r") as file:
#         data = yaml.safe_load(file)

#     instances = data.get("instances", {})
#     discovered_relationships_data = []

#     # Extract discovered relationships
#     for instance_name, instance_data in instances.items():
#         source_uri = instance_data.get("uri")
#         log_message(f"Processing instance: {instance_name} ({source_uri})", "INFO")

#         # Process discovered relationships
#         discovered_relationships = instance_data.get("discoveredRelationships", {}).get("hasRelationshipWith", [])
#         for relationship in discovered_relationships:
#             target_entity = relationship.get("relatedEntity", {})
#             relationship_type = relationship.get("relationshipType", "RELATIONSHIP")
#             source = relationship.get("source", {})

#             discovered_relationships_data.append({
#                 "source": {"uri": source_uri},
#                 "target": target_entity,
#                 "type": relationship_type,
#                 "source_details": source
#             })

#     # Upload discovered relationships to Neo4j
#     log_message(f"Found {len(discovered_relationships_data)} relationships to upload.", "INFO")
#     upload_discovered_relationships(discovered_relationships_data)


# def upload_discovered_relationships(relationships):
#     """
#     Upload discovered relationships to Neo4j.
#     """
#     with driver.session() as session:
#         for relationship in relationships:
#             source_uri = relationship['source']['uri']
#             target_uri = relationship['target']['uri']
#             relationship_type = relationship['type']
#             source_details = relationship.get('source_details', {})
#             source_id = source_details.get('source_id', "")
#             quote_id = source_details.get('quote_id', "")
#             confidence_score = source_details.get('confidence_score', 1.0)
#             feed = source_details.get('feed', "manual")

#             try:
#                 session.write_transaction(
#                     create_discovered_relationship,
#                     source_uri,
#                     target_uri,
#                     relationship_type,
#                     confidence_score,
#                     source_id,
#                     quote_id,
#                     feed
#                 )
#                 log_message(f"Created relationship: ({source_uri}) -[:{relationship_type}]-> ({target_uri})", "INFO")
#             except Exception as e:
#                 log_message(f"Failed to create relationship: ({source_uri}) -[:{relationship_type}]-> ({target_uri}). Error: {str(e)}", "ERROR")


# def create_discovered_relationship(tx, source_uri, target_uri, relationship_type, confidence_score, source_id, quote_id, feed):
#     """
#     Create a unidirectional discovered relationship between two nodes.
#     """
#     query = f"""
#     MATCH (source {{uri: $source_uri}}), (target {{uri: $target_uri}})
#     MERGE (source)-[r:{relationship_type}]->(target)
#     SET r += {{
#         confidence_score: $confidence_score,
#         source_id: $source_id,
#         quote_id: $quote_id,
#         feed: $feed
#     }}
#     """
#     tx.run(
#         query,
#         source_uri=source_uri,
#         target_uri=target_uri,
#         confidence_score=confidence_score,
#         source_id=source_id,
#         quote_id=quote_id,
#         feed=feed
#     )


# # Example usage
# if __name__ == "__main__":
#     yaml_file_path = "/Users/fede/Desktop/git/monsieur_neo/ontologies/magicHourEntity.yaml"
#     try:
#         log_message("Starting upload process...", "INFO")
#         upload_data_from_yaml(yaml_file_path)
#         log_message("Relationships added successfully!", "INFO")
#     except Exception as e:
#         log_message(f"An error occurred: {str(e)}", "ERROR")
#     finally:
#         driver.close()
#         log_message("Neo4j driver closed.", "INFO")
