import yaml
from rdflib import Graph, Namespace, RDF, URIRef, Literal
from rdflib.namespace import XSD

# Define namespaces
monsieur = Namespace("http://monsieur.org/ontology#")

# Initialize graph
g = Graph()
g.bind("monsieur", monsieur)

# Load YAML file
yaml_file = "/Users/federico/Desktop/Hermetic Library/monsieur_neo/ontologies/magicHourEntity.yaml"  # Replace with your file path
with open(yaml_file, 'r') as file:
    data = yaml.safe_load(file)

# Process each item in the YAML file
instances = data.get('instances', {})
for hour, details in instances.items():
    hour_uri = URIRef(details['uri'])

    # Create the MagicHour instance
    g.add((hour_uri, RDF.type, URIRef(monsieur.MagicHour)))

    # Add basic properties
    g.add((hour_uri, URIRef(monsieur.name), Literal(details['defaultProperties']['hasName'], datatype=XSD.string)))
    g.add((hour_uri, URIRef(monsieur.image), Literal(details['defaultProperties']['hasImage'], datatype=XSD.string)))
    g.add((hour_uri, URIRef(monsieur.synonyms), Literal(", ".join(details['defaultProperties']['hasSynonyms']), datatype=XSD.string)))
    
    # Add definition property
    description = details.get('description', "")  # Fallback to empty string if description is missing
    g.add((hour_uri, URIRef(monsieur.definition), Literal(description, datatype=XSD.string)))

    # Add discovered relationships
    for relationship in details['discoveredRelationships']['hasRelationshipWith']:
        relationship_type = relationship['relationshipType']
        related_entity_label = relationship['relatedEntity']['label']
        related_entity_uri = URIRef("#" + related_entity_label)
        if relationship_type == "hour_ruled_by":
            g.add((hour_uri, URIRef(monsieur.hour_ruled_by), related_entity_uri))
        elif relationship_type == "is_part_of_day":
            g.add((hour_uri, URIRef(monsieur.is_part_of_day), related_entity_uri))

# Save the graph to an OWL file
owl_file = "/Users/federico/Desktop/Hermetic Library/monsieur_neo/ontologies/magicHourEntity.owl"
g.serialize(destination=owl_file, format="xml")

print(f"OWL file has been generated and saved as {owl_file}.")
