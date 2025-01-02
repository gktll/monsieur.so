from app.routes.constants import neo4j_driver
from app.routes.utils.ephemeris_calculator import EphemerisCalculator
from app.routes.constants import ORDINAL_NAMES


class Neo4jQueries:
    """
    Class to handle Neo4j queries related to planetary hours and geolocation data.
    """

    def __init__(self, ephemeris_calculator: EphemerisCalculator = None):
        self.driver = neo4j_driver  # Initialize Neo4j driver from constants
        self.ephemeris_calculator = ephemeris_calculator  # Optional dependency
        print(f"DEBUG: Initialized Neo4jQueries with EphemerisCalculator: {self.ephemeris_calculator}")


    def format_hour_name(self, hour_index):
        """
        Format hour name for Neo4j query.
        
        Args:
            hour_index (int): Hour number (1 to 12 for day, -1 to -12 for night)
                            Negative numbers automatically become Night hours
        """
        if not self.ephemeris_calculator:
            raise ValueError("EphemerisCalculator is required to format hour names.")
        
        # Use absolute value to get the ordinal name (converts -4 to 4th, etc)
        ordinal_idx = abs(hour_index)
        # Use sign to determine day/night (negative becomes Night)
        day_segment = 'Day' if hour_index > 0 else 'Night'
        weekday = self.ephemeris_calculator.now_local.strftime('%A')
        
        # This creates URIs like "Hour_4th_Of_Night_Wednesday" from -4
        # or "Hour_4th_Of_Day_Wednesday" from 4
        return f"Hour_{ORDINAL_NAMES[ordinal_idx - 1]}_Of_{day_segment}_{weekday}"
    

    def fetch_hour_data(self, hour_name, planetary_positions):
        """
        Fetch and process Neo4j data for the given hour.
        """
        with self.driver.session() as session:
            query = f"""
            MATCH (hour {{uri: "monsieur:MagicHourEntity/{hour_name}"}})
            OPTIONAL MATCH (hour)-[r]-(connectedNode)
            RETURN 
                hour,
                type(r) AS relationshipType,
                connectedNode,
                properties(r) AS relationshipProperties,
                labels(connectedNode) AS nodeLabels,
                properties(connectedNode) AS nodeProperties
            """
            results = [record.data() for record in session.run(query)]

            simplified = {
                "hour": None,
                "connections": []
            }

            for record in results:
                if not simplified["hour"]:
                    simplified["hour"] = {
                        "label": record["hour"].get("hasName") or record["hour"].get("label"),
                        "description": record["hour"].get("description"),
                        "uri": record["hour"].get("uri"),
                        **planetary_positions
                    }

                if record.get("relationshipType") == "HAS_MEMBER":
                    continue

                if record.get("connectedNode"):
                    connection = {
                        "relationshipType": record["relationshipType"],
                        "targetNode": {
                            "label": (record["connectedNode"].get("hasName") or 
                                      record["connectedNode"].get("label") or 
                                      record["connectedNode"].get("description") or 
                                      record["connectedNode"].get("uri")),
                            "description": record["connectedNode"].get("description"),
                            "uri": record["connectedNode"].get("uri"),
                            "type": record["nodeLabels"],
                        },
                        "relationshipProperties": record.get("relationshipProperties", {})
                    }
                    simplified["connections"].append(connection)
                    
                    # Extract hour ruling planet from HOURS_RULED_BY relationship
                    if connection["relationshipType"] == "HOURS_RULED_BY" and "PlanetEntity" in connection["targetNode"]["uri"]:
                        simplified["hour_ruler"] = connection["targetNode"]["label"]

            return simplified
    


    def fetch_hour_graph(self, hour_name):
        """
        Fetch hour-related network graph data for visualization.
        """
        with self.driver.session() as session:
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
            results = session.run(query, hour_uri=hour_name)
            return [record.data() for record in results]



    # Placeholder for additional queries
    def query_planetary_data(self, planetary_positions):
        pass

    def query_aspects(self, planet_name):
        pass

    def query_natal_chart(self, user_id):
        pass