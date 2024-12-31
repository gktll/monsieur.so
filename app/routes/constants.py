from neo4j import GraphDatabase
from skyfield.api import load

# Neo4j configuration
NEO4J_URI = "neo4j+s://eb32f100.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "DGXWFgCX7QiAMLk-6ZSJs7ZZwGN7PM1Ps7F6Jh6-eGw"
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

