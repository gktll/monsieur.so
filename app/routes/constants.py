from neo4j import GraphDatabase
from skyfield.api import load
from dotenv import load_dotenv
import os

# Neo4j configuration
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise ValueError("Neo4j connection details are missing in the environment variables.")

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# Load ephemerides once
ephemeris = load('de440s.bsp')
ts = load.timescale()

# Planetary Order
PLANETARY_ORDER = ['Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter', 'Mars']
EXTENDED_PLANETARY_ORDER = PLANETARY_ORDER + ['Uranus', 'Neptune', 'Pluto']

DAY_RULERS = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']

ORDINAL_NAMES = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', 
                 '8th', '9th', '10th', '11th', '12th']

# Skyfield Identifiers
SKYFIELD_IDS = {
    'Sun': 'sun',
    'Moon': 'moon',
    'Mercury': 'mercury barycenter',
    'Venus': 'venus barycenter',
    'Mars': 'mars barycenter',
    'Jupiter': 'jupiter barycenter',
    'Saturn': 'saturn barycenter'
}

EXTENDED_SKYFIELD_IDS = {
    **SKYFIELD_IDS,
    'Uranus': 'uranus barycenter',
    'Neptune': 'neptune barycenter',
    'Pluto': 'pluto barycenter'
}

DEFAULT_ASPECT_CONFIG = {
    "Conjunction": {"angle": 0, "orb": 8},
    "Opposition": {"angle": 180, "orb": 8},
    "Square": {"angle": 90, "orb": 7},
    "Trine": {"angle": 120, "orb": 7},
    "Sextile": {"angle": 60, "orb": 6},
}

# Essential dignities
ESSENTIAL_DIGNITIES = {
    'Sun': {'rulership': 'Leo', 'exaltation': 'Aries', 'detriment': 'Aquarius', 'fall': 'Libra'},
    'Moon': {'rulership': 'Cancer', 'exaltation': 'Taurus', 'detriment': 'Capricorn', 'fall': 'Scorpio'},
    'Mercury': {'rulership': 'Gemini', 'exaltation': 'Virgo', 'detriment': 'Sagittarius', 'fall': 'Pisces'},
    'Venus': {'rulership': 'Taurus', 'exaltation': 'Pisces', 'detriment': 'Scorpio', 'fall': 'Virgo'},
    'Mars': {'rulership': 'Aries', 'exaltation': 'Capricorn', 'detriment': 'Libra', 'fall': 'Cancer'},
    'Jupiter': {'rulership': 'Sagittarius', 'exaltation': 'Cancer', 'detriment': 'Gemini', 'fall': 'Capricorn'},
    'Saturn': {'rulership': 'Capricorn', 'exaltation': 'Libra', 'detriment': 'Cancer', 'fall': 'Aries'},
    'Uranus': {'rulership': 'Aquarius', 'exaltation': 'Scorpio', 'detriment': 'Leo', 'fall': 'Taurus'},
    'Neptune': {'rulership': 'Pisces', 'exaltation': 'Leo', 'detriment': 'Virgo', 'fall': 'Capricorn'},
    'Pluto': {'rulership': 'Scorpio', 'exaltation': 'Aries', 'detriment': 'Taurus', 'fall': 'Libra'}
}

# Zodiac Signs
ZODIAC_SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

# Planetary Colors
PLANETARY_COLORS = {
    "Sun": "#F2FF00",       # Yellow
    "Moon": "#D7DEDC",      # White + Silver
    "Mercury": "#7C00FE",   # Purple
    "Venus": "#51CB20",     # Green
    "Mars": "#F5004F",      # Red
    "Jupiter": "#072AC8",   # Blue
    "Saturn": "#241909",    # Black
    "Uranus": "#769FB6",    # Pale Blue
    "Neptune": "#F9C7FA",   # Lilac
    "Pluto": "#D4B9B0"      # Beige
}

