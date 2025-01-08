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
    'Mercury': 'mercury',
    'Venus': 'venus',
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


PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '⛢',
    'Neptune': '♆',
    'Pluto': '♇'
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


TRIPLICITIES = {
    'Aries': 'Fire',
    'Taurus': 'Water',
    'Gemini': 'Air',
    'Cancer': 'Earth',
    'Leo': 'Fire',
    'Virgo': 'Water',
    'Libra': 'Air',
    'Scorpio': 'Earth',
    'Sagittarius': 'Fire', 
    'Carpicorn': 'Water',
    'Aquarius': 'Air',
    'Pisces': 'Earth'     
}


SIGN_SYMBOLS = {
    'Aries': '♈︎',
    'Taurus': '♉︎',
    'Gemini': '♊︎',
    'Cancer': '♋︎',
    'Leo': '♌︎',
    'Virgo': '♍︎',
    'Libra': '♎︎',
    'Scorpio': '♏︎',
    'Sagittarius': '♐︎', 
    'Carpicorn': '♑︎',
    'Aquarius': '♒︎',
    'Pisces': '♓︎'     
}


# Planetary Colors with gradient definitions
PLANETARY_COLORS = {
    "Sun": {
        "gradient_stops": {
            "core": "#F2FF00",   # Full yellow
            "inner": "#FFF7B0",  # Lighter yellow
            "outer": "#FFFFD0"   # Very light yellow/white
        }
    },
    "Moon": {
        "gradient_stops": {
            "core": "#D7DEDC",   # Silver
            "inner": "#E8ECEB",  # Lighter silver
            "outer": "#F9FAFA"   # Almost white
        }
    },
    "Mercury": {
        "gradient_stops": {
            "core": "#7C00FE",   # Deep purple
            "inner": "#9E40FE",  # Medium purple
            "outer": "#C080FE"   # Light purple
        }
    },
    "Venus": {
        "gradient_stops": {
            "core": "#51CB20",   # Bright green
            "inner": "#7DDB56",  # Lighter green
            "outer": "#A9EB8C"   # Very light green
        }
    },
    "Mars": {
        "gradient_stops": {
            "core": "#F5004F",   # Deep red
            "inner": "#F74979",  # Medium red
            "outer": "#F993A3"   # Light red
        }
    },
    "Jupiter": {
        "gradient_stops": {
            "core": "#072AC8",   # Deep blue
            "inner": "#2955D6",  # Medium blue
            "outer": "#4B80E4"   # Light blue
        }
    },
    "Saturn": {
        "gradient_stops": {
            "core": "#0A0A0A",   # Night black
            "inner": "#1F1F1F",  # Eeerie Black 
            "outer": "#333333"   # Jet
        }
    },
    "Uranus": {
        "gradient_stops": {
            "core": "#769FB6",   # Pale blue
            "inner": "#97B8CA",  # Lighter pale blue
            "outer": "#B8D1DE"   # Very light pale blue
        }
    },
    "Neptune": {
        "gradient_stops": {
            "core": "#F9C7FA",   # Lilac
            "inner": "#FBD9FC",  # Light lilac
            "outer": "#FDEBFE"   # Very light lilac
        }
    },
    "Pluto": {
        "gradient_stops": {
            "core": "#D4B9B0",   # Beige
            "inner": "#E1CCC5",  # Light beige
            "outer": "#EEE0DA"   # Very light beige
        }
    }
}

PLANET_DIAMETERS = {
    'Sun': 1392000,
    'Mercury': 4879,
    'Venus': 12104,
    'Earth': 12742,
    'Mars': 6779,
    'Jupiter': 139820,
    'Saturn': 116460,
    'Uranus': 50724,
    'Neptune': 49244,
    'Pluto': 2376,
    'Moon': 3475
}