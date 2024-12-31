from py2neo import Graph, Node, Relationship
import uuid
from datetime import datetime
from enum import Enum


class SpiritualEntityType(Enum):
    ANGEL = ("Angel", "#FFD700")  # Gold
    DEMON = ("Demon", "#8B0000")  # Dark Red
    ELEMENTAL = ("Elemental", "#4682B4")  # Steel Blue
    FAMILIAR_SPIRIT = ("Familiar Spirit", "#708090")
    POLTERGEIST_SPIRIT = ("Familiar Spirit", "#cccccc")  

    def __init__(self, type_name, color):
        self.type_name = type_name
        self.color = color

    @property
    def display_name(self):
        return self.type_name

    @property
    def color_code(self):
        return self.color
    

def create_spiritual_entity(self, name, entity_type: SpiritualEntityType, description=None, image=None):
    """
    Creates or updates a spiritual entity node in the Neo4j database.
    """
    if not isinstance(entity_type, SpiritualEntityType):
        raise ValueError(f"Invalid entity type: {entity_type}. Must be one of {[e.display_name for e in SpiritualEntityType]}")

    # Check if an entity with the same name and type already exists
    entity_node = self.graph.nodes.match("SpiritualEntity", name=name).first()
    
    if entity_node:
        # Update the existing node
        entity_node.update({
            "type": entity_type.display_name,
            "color": entity_type.color_code,
            "description": description,
            "image": image,
            "updated_at": datetime.now()
        })
        self.graph.push(entity_node)
    else:
        # Create a new node
        entity_node = Node(
            "SpiritualEntity",
            id=str(uuid.uuid4()),
            name=name,
            type=entity_type.display_name,
            color=entity_type.color_code,
            description=description,
            image=image,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.graph.create(entity_node)
    
    return entity_node


class AstrologyEntityType(Enum):
    STAR = ("Star", "#")  # Gold
    PLANET = ("Planet", "#")  # Dark Red
    ZODIACAL_SIGN = ("Zodiacal Sign", "#")  # Steel Blue
    CONSTELLATION = ("Constellation", "#")  # Slate Gray

    def __init__(self, type_name, color):
        self.type_name = type_name
        self.color = color

    @property
    def display_name(self):
        return self.type_name

    @property
    def color_code(self):
        return self.color
    
def create_substance_entity(self, name, entity_type: AstrologyEntityType, description=None, image=None, symbol=symbol):
    """
    Creates or updates a spiritual entity node in the Neo4j database.
    """
    if not isinstance(entity_type, AstrologyEntityType):
        raise ValueError(f"Invalid entity type: {entity_type}. Must be one of {[e.display_name for e in AstrologyEntityType]}")

    # Check if an entity with the same name and type already exists
    entity_node = self.graph.nodes.match("AstrologyEntity", name=name).first()
    
    if entity_node:
        # Update the existing node
        entity_node.update({
            "type": entity_type.display_name,
            "color": entity_type.color_code,
            "description": description,
            "image": image,
            "symbol": symbol,
            "updated_at": datetime.now()
        })
        self.graph.push(entity_node)
    else:
        # Create a new node
        entity_node = Node(
            "SpiritualEntity",
            id=str(uuid.uuid4()),
            name=name,
            type=entity_type.display_name,
            color=entity_type.color_code,
            description=description,
            image=image,
            symbol=symbol,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.graph.create(entity_node)
    
    return entity_node













class AlchemyEntityType(Enum):
    RECIPE = ("recipe", "#")  # Gold
    EQUIPMENT = ("Equipment", "#")  # Dark Red
    STAGE = ("Stage", "#")  # Steel Blue
    PROCESS = ("Process", "#")  # Slate Gray

    def __init__(self, type_name, color):
        self.type_name = type_name
        self.color = color

    @property
    def display_name(self):
        return self.type_name

    @property
    def color_code(self):
        return self.color


class SubstanceEntityType(Enum):
    MINERAL = ("Mineral", "#")  # Gold
    METAL = ("Metal", "#")  # Dark Red
    ORGANIC_PLANT = ("Stage", "#")  # Steel Blue
    PROCESS = ("Process", "#")  # Slate Gray

    def __init__(self, type_name, color):
        self.type_name = type_name
        self.color = color

    @property
    def display_name(self):
        return self.type_name

    @property
    def color_code(self):
        return self.color


def create_substance_entity(self, name, entity_type: SubstanceEntityType, description=None, image=None, synonyms=none):
    """
    Creates or updates a spiritual entity node in the Neo4j database.
    """
    if not isinstance(entity_type, SubstanceEntityType):
        raise ValueError(f"Invalid entity type: {entity_type}. Must be one of {[e.display_name for e in SubstanceEntityType]}")

    # Check if an entity with the same name and type already exists
    entity_node = self.graph.nodes.match("SubstanceEntity", name=name).first()
    
    if entity_node:
        # Update the existing node
        entity_node.update({
            "type": entity_type.display_name,
            "color": entity_type.color_code,
            "description": description,
            "image": image,
            "synonyms": synonyms,
            "updated_at": datetime.now()
        })
        self.graph.push(entity_node)
    else:
        # Create a new node
        entity_node = Node(
            "SpiritualEntity",
            id=str(uuid.uuid4()),
            name=name,
            type=entity_type.display_name,
            color=entity_type.color_code,
            description=description,
            image=image,
            synonyms=synonyms,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.graph.create(entity_node)
    
    return entity_node



















def add_dynamic_relationship(self, entity_id, related_entity_id, relationship_type, source=None):
    """
    Adds or updates a dynamic relationship between two spiritual entities.
    Each entity can have custom relationships like 'conflicts_with', 'precedes', 'guides', etc.
    """
    # Match the two nodes based on their IDs
    entity_node = self.graph.nodes.match("SpiritualEntity", id=entity_id).first()
    related_entity_node = self.graph.nodes.match("SpiritualEntity", id=related_entity_id).first()
    
    if entity_node and related_entity_node:
        # Create or update the relationship with optional source tracking
        rel = Relationship(entity_node, relationship_type, related_entity_node)
        if source:
            rel["source"] = source
        rel["created_at"] = datetime.now()
        
        self.graph.create(rel)  # Sa