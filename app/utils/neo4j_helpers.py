
from neo4j import GraphDatabase

# Neo4j Driver Initialization
NEO4J_URI = "neo4j+s://eb32f100.databases.neo4j.io"  
NEO4J_USER = "neo4j"               
NEO4J_PASSWORD = "DGXWFgCX7QiAMLk-6ZSJs7ZZwGN7PM1Ps7F6Jh6-eGw"            

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def format_hour_name(hour_index, day_segment, weekday_name):
    """
    Format the hour name with capitalized components for Neo4j.
    
    Args:
        hour_index (int): 1-based hour index.
        day_segment (str): 'day' or 'night'.
        weekday_name (str): Weekday name in lowercase ('monday', etc.).
    
    Returns:
        str: Formatted hour name (e.g., "Hour_2nd_Of_Night_Monday").
    """
    ordinal_names = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', 
                     '8th', '9th', '10th', '11th', '12th']
    hour_ordinal = ordinal_names[hour_index - 1]  # Correct ordinal formatting
    capitalized_day_segment = day_segment.capitalize()  # Capitalize "Day" or "Night"
    capitalized_weekday = weekday_name.capitalize()  # Capitalize "Monday", etc.
    formatted_name = f"Hour_{hour_ordinal}_Of_{capitalized_day_segment}_{capitalized_weekday}"
    print(f"DEBUG: Formatted hour name: {formatted_name}")
    return formatted_name


def fetch_hour_data(hour_name, neo4j_driver):
    """
    Query Neo4j for the specific hour with capitalized URIs.
    
    Args:
        hour_name (str): Formatted hour name (e.g., "Hour_2nd_Of_Night_Monday").
        neo4j_driver (GraphDatabase.driver): Initialized Neo4j driver.
    
    Returns:
        list: Simplified results of Neo4j query.
    """
    print(f"DEBUG: Fetching Neo4j data for hour_name: {hour_name}")
    with neo4j_driver.session() as session:
        query = f"""
        MATCH (hour {{uri: "monsieur:MagicHourEntity/{hour_name}"}})
        OPTIONAL MATCH (hour)-[r]-(connectedNode)
        WHERE NOT "MagicHourEntity" IN labels(connectedNode)
        RETURN 
            hour,
            type(r) AS relationshipType,
            connectedNode,
            properties(r) AS relationshipProperties,
            labels(connectedNode) AS nodeLabels,
            properties(connectedNode) AS nodeProperties
        """
        print(f"DEBUG: Executing query:\n{query}")
        results = session.run(query)
        print(f"DEBUG: Query executed. Results fetched.")
        data = [record.data() for record in results]
        print(f"DEBUG: Results processed: {data}")
        simplified_data = simplify_neo4j_results(data)
        return simplified_data


def simplify_neo4j_results(data):
    """
    Simplify Neo4j results to include only relevant fields.
    
    Args:
        data (list): Raw Neo4j query results.
    
    Returns:
        dict: Simplified and structured data.
    """
    simplified = {
        "hour": None,
        "connections": []
    }

    for record in data:
        # Extract hour data once
        if not simplified["hour"] and "hour" in record:
            simplified["hour"] = {
                "label": record["hour"].get("hasName"),
                "description": record["hour"].get("description"),
                "uri": record["hour"].get("uri")
            }

        # Add connections
        connection = {
            "relationshipType": record["relationshipType"],
            "targetNode": {
                "label": record["connectedNode"].get("hasName"),
                "description": record["connectedNode"].get("description"),
                "uri": record["connectedNode"].get("uri"),
                "type": record["nodeLabels"]
            },
            "relationshipProperties": record.get("relationshipProperties", {})
        }
        simplified["connections"].append(connection)
    
    print(f"DEBUG: Simplified results: {simplified}")
    return simplified
