
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone as dt_timezone
from pytz import timezone as pytz_timezone
from skyfield.api import wgs84
from skyfield.almanac import find_discrete, sunrise_sunset
import swisseph as swe
import numpy as np
from timezonefinder import TimezoneFinder
import math
import uuid

from app.routes.constants import PLANETARY_ORDER, DAY_RULERS, ZODIAC_SIGNS, PLANETARY_COLORS, ORDINAL_NAMES, SKYFIELD_IDS, ESSENTIAL_DIGNITIES, EXTENDED_PLANETARY_ORDER, EXTENDED_SKYFIELD_IDS
from app.routes.constants import ephemeris, ts
from app.routes.constants import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, neo4j_driver


# Utility Functions for Calculating Moon's illumination's percentage
def calculate_moon_illumination(phase_angle):
    """
    Calculate the percentage of the Moon's surface that is illuminated.
    
    Args:
        phase_angle (float): The phase angle between the Moon and Sun in degrees.
        
    Returns:
        float: The percentage of the Moon's surface that is illuminated.
    """
    # Convert phase angle to radians
    phase_angle_radians = math.radians(phase_angle)
    
    # Apply the formula for illumination percentage
    illumination_percentage = (1 + math.cos(phase_angle_radians)) / 2 * 100
    
    return round(illumination_percentage, 2)




# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# EPHEMERIS CALCULATOR CLASS
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

class EphemerisCalculator:
    
    OBLIQUITY = math.radians(23.4367)  # Earth's axial tilt

    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.observer = wgs84.latlon(latitude, longitude)
        
        # Initialize timezone
        tz_finder = TimezoneFinder()
        self.timezone_name = tz_finder.timezone_at(lat=latitude, lng=longitude)
        if not self.timezone_name:
            raise ValueError("Could not determine timezone for the given location.")
        self.timezone = pytz_timezone(self.timezone_name)
        
        # Initialize times
        self.now_utc = datetime.now(dt_timezone.utc)
        self.now_local = self.now_utc.astimezone(self.timezone)
        
        # Calculate sun times once
        self.sunrise_local, self.sunset_local = self._calculate_sun_times()


    # ---------------------------------------------
    # CALCULATE SUNTIME BASING ON LAT / LONG
    # ---------------------------------------------

    def _calculate_sun_times(self):
        """
        Calculate sunrise and sunset times.
        """
        f = sunrise_sunset(ephemeris, self.observer)
        local_date = self.now_local.date()
        
        t0 = ts.utc(local_date.year, local_date.month, local_date.day)
        t1 = ts.utc(local_date.year, local_date.month, local_date.day, 23, 59, 59)
        
        times, events = find_discrete(t0, t1, f)
        sunrise_indices = np.where(events == 0)[0]
        sunset_indices = np.where(events == 1)[0]
        
        if not sunrise_indices.size or not sunset_indices.size:
            raise ValueError("Could not determine sunrise or sunset times.")
            
        sunrise_utc = times[sunrise_indices[0]].utc_datetime()
        sunset_utc = times[sunset_indices[-1]].utc_datetime()
        
        sunrise_local = sunrise_utc.replace(tzinfo=dt_timezone.utc).astimezone(self.timezone)
        sunset_local = sunset_utc.replace(tzinfo=dt_timezone.utc).astimezone(self.timezone)
        
        if sunrise_local > sunset_local:
            sunrise_local, sunset_local = sunset_local, sunrise_local
            
        return sunrise_local, sunset_local
    


    # ---------------------------------------------
    # CALCULATE CURRENT PLANETARY HOUR 
    # ---------------------------------------------

    def calculate_planetary_hour(self):
        """
        Calculate current planetary hour and ruling planet.
        """
        if self.sunrise_local <= self.now_local <= self.sunset_local:
            duration = (self.sunset_local - self.sunrise_local).total_seconds() / 12
            time_since_sunrise = (self.now_local - self.sunrise_local).total_seconds()
            hour_index = int(time_since_sunrise // duration)
        else:
            next_sunrise_local = self.sunrise_local + timedelta(days=1)
            duration = (next_sunrise_local - self.sunset_local).total_seconds() / 12
            time_since_sunset = (self.now_local - self.sunset_local).total_seconds()
            hour_index = int(time_since_sunset // duration)
            
        day_index = self.now_local.weekday()
        day_ruling_planet = DAY_RULERS[day_index]
        start_planet_index = PLANETARY_ORDER.index(day_ruling_planet)
        ruling_planet = PLANETARY_ORDER[(start_planet_index + hour_index) % len(PLANETARY_ORDER)]
        
        return hour_index, ruling_planet
    


    # ---------------------------------------------
    # CALCULATE CURRENT PLANETARY POSITIONS 
    # ---------------------------------------------

    def calculate_planetary_positions(self):
        """
        Calculate positions for all planets, including ecliptic coordinates, altitude, and azimuth.
        Check for Retrograde, Stationary motions, and Out-of-Bound (OOB) status.
        """
        positions = {}
        observer_time = ts.from_datetime(self.now_utc)
        observer_time_tomorrow = ts.from_datetime(self.now_utc + timedelta(days=1))
        
        earth = ephemeris['earth']
        topos = earth + self.observer

        # Combine inner and outer planets
        extended_planetary_order = PLANETARY_ORDER + ['Uranus', 'Neptune', 'Pluto']
        extended_skyfield_ids = {
            **SKYFIELD_IDS,
            'Uranus': 'uranus barycenter',
            'Neptune': 'neptune barycenter',
            'Pluto': 'pluto barycenter'
        }
        
        for planet_name in extended_planetary_order:
            try:
                planet = ephemeris[extended_skyfield_ids[planet_name]]

                # Calculate ecliptic position
                astrometric = topos.at(observer_time).observe(planet)
                ecliptic_pos = astrometric.ecliptic_latlon()
                position = float(ecliptic_pos[1].degrees)

                # Calculate tomorrow's position for retrograde/stationary check
                astrometric_tomorrow = topos.at(observer_time_tomorrow).observe(planet)
                ecliptic_pos_tomorrow = astrometric_tomorrow.ecliptic_latlon()
                position_tomorrow = float(ecliptic_pos_tomorrow[1].degrees)

                # Calculate daily motion
                daily_motion = position_tomorrow - position
                if daily_motion > 180:
                    daily_motion -= 360
                elif daily_motion < -180:
                    daily_motion += 360

                # Normalize position
                position = position % 360
                if position < 0:
                    position += 360

                # Check for retrograde and stationary
                is_retrograde = daily_motion < 0
                is_stationary = abs(daily_motion) < 0.01  # Threshold for stationary (0.01° per day)

                sign_index = int(position // 30)
                sign_degree = position % 30

                # Calculate altitude and azimuth
                alt, az, _ = astrometric.apparent().altaz()
                
                positions[planet_name] = {
                    "longitude": round(position, 2),
                    "sign": ZODIAC_SIGNS[sign_index],
                    "degree": round(sign_degree, 2),
                    "is_retrograde": is_retrograde,
                    "is_stationary": is_stationary,
                    "daily_motion": round(daily_motion, 4),
                    "altitude": round(alt.degrees, 2),
                    "azimuth": round(az.degrees, 2),
                }

                # Add Moon-specific distance (AU and KM)
                if planet_name == 'Moon':
                    distance_au = astrometric.distance().au
                    positions['Moon']["distance_au"] = round(distance_au, 6)
                    positions['Moon']["distance_km"] = round(distance_au * 149597870.7, 2)  # Convert AU to KM

            except Exception as e:
                print(f"Error calculating {planet_name}: {e}")
                positions[planet_name] = {
                    "longitude": 0,
                    "sign": "Unknown",
                    "degree": 0,
                    "is_retrograde": False,
                    "is_stationary": False,
                    "daily_motion": 0.0,
                    "altitude": 0.0,
                    "azimuth": 0.0,
                    "error": f"Calculation failed: {e}"
                }
        
        self.planetary_positions = positions  # Assign to instance
        return positions


    # ------------------------------------------------------
    # CALCULATE PLANETARY DISTANCES FROM EARTH / OBSERVER 
    # -------------------------------------------------------

    def calculate_planetary_distances(self):
        """
        Calculate the distance of each planet (including outer planets) from Earth using Skyfield.
        
        Returns:
            dict: A dictionary with planet names as keys and their distances (in AU) as values.
        """
        observer_time = ts.from_datetime(self.now_utc)  # Use the current UTC time
        distances = {}

        earth = ephemeris['earth']
        for planet_name, skyfield_id in EXTENDED_SKYFIELD_IDS.items():  # Use extended IDs
            try:
                planet_obj = ephemeris[skyfield_id]
                # Calculate distance from Earth
                distance = earth.at(observer_time).observe(planet_obj).distance().au
                distances[planet_name] = round(distance, 6)  # Round to 6 decimal places for precision
            except Exception as e:
                distances[planet_name] = {"error": f"Failed to calculate distance: {str(e)}"}

        return distances



    # ------------------------------------------------------
    # CALCULATE COMBUSTION / CAZIMI / OUT OF BOUND
    # -------------------------------------------------------

    def calculate_combustion_and_cazimi(self):
        """
        Calculate combustion and cazimi for planets relative to the Sun.
        Uses precomputed planetary positions from calculate_planetary_positions.
        
        MISSING! Calculate out of bound for all planets.
        """
        # Calculate planetary positions if not already done
        positions = self.calculate_planetary_positions()
        
        # Retrieve Sun's longitude
        sun_longitude = positions.get("Sun", {}).get("longitude")
        if sun_longitude is None:
            raise ValueError("Sun's position is required for combustion and cazimi calculations.")

        results = {}

        for planet, data in positions.items():
            if planet == "Sun":  # Skip the Sun itself
                continue

            # Use precomputed longitude for each planet
            planet_longitude = data["longitude"]
            angular_distance = abs(planet_longitude - sun_longitude)

            # Normalize angular distance to ensure it doesn't exceed 180°
            if angular_distance > 180:
                angular_distance = 360 - angular_distance

            # Determine combustion and cazimi
            is_combust = angular_distance <= 8.5
            is_cazimi = angular_distance <= 0.283

            results[planet] = {
                "is_combust": is_combust,
                "is_cazimi": is_cazimi,
                "angular_distance": round(angular_distance, 2)
            }

        return results
    


    # ------------------------------------------------------------------
    # CALCULATE ASPECTS [OPPOSITION, CONJUCTION, TRINE, SQUARE, SEXTILE]
    # -------------------------------------------------------------------

    def calculate_aspects(self, aspect_config=None):
        """
        Calculate aspects between planets based on their longitudes.

        Args:
            aspect_config (dict, optional): Aspect angles and their allowable orbs.

        Returns:
            list: List of aspects, including the two planets involved and their relationship.
        """
        # Compute planetary positions internally
        positions = self.calculate_planetary_positions()

        # Default aspect configuration if not provided
        if aspect_config is None:
            aspect_config = {
                "Conjunction": {"angle": 0, "orb": 8},
                "Opposition": {"angle": 180, "orb": 8},
                "Square": {"angle": 90, "orb": 7},
                "Trine": {"angle": 120, "orb": 7},
                "Sextile": {"angle": 60, "orb": 6},
            }

        aspects = []

        # Get list of planets to compare
        planets = list(positions.keys())

        # Iterate over all unique pairs of planets
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1, planet2 = planets[i], planets[j]
                pos1, pos2 = positions[planet1]["longitude"], positions[planet2]["longitude"]

                # Calculate angular distance
                angular_distance = abs(pos1 - pos2)
                if angular_distance > 180:
                    angular_distance = 360 - angular_distance

                # Check for aspects
                for aspect_name, config in aspect_config.items():
                    angle, orb = config["angle"], config["orb"]
                    if abs(angular_distance - angle) <= orb:
                        aspects.append({
                            "planet1": planet1,
                            "planet2": planet2,
                            "aspect": aspect_name,
                            "angular_distance": round(angular_distance, 2),
                        })

        return aspects



    # ------------------------------------------------------------------
    # CALCULATE MOON SPECIFIC PROPERTIES
    # -------------------------------------------------------------------

    def calculate_moon_properties(self, positions=None):
        """
        Calculate detailed properties of the Moon, reusing precomputed data if available.

        Args:
            positions (dict, optional): Precomputed planetary positions. If not provided,
                                        positions are computed internally.

        Returns:
            dict: Detailed Moon properties (phase, distance, declination, etc.).
        """
        # Reuse precomputed positions or calculate internally
        if positions is None:
            positions = self.calculate_planetary_positions()

        # Ensure Moon's data is available
        moon_data = positions.get("Moon")
        if not moon_data:
            raise ValueError("Moon's position is not available in planetary positions.")

        # Calculate the Sun's position
        sun_longitude = positions.get("Sun", {}).get("longitude")
        if not sun_longitude:
            raise ValueError("Sun's position is required for Moon phase calculations.")

        # Calculate phase angle
        moon_longitude = moon_data["longitude"]
        moon_phase_angle = abs(moon_longitude - sun_longitude)
        if moon_phase_angle > 180:
            moon_phase_angle = 360 - moon_phase_angle

        # Calculate illumination percentage
        illumination_percentage = calculate_moon_illumination(moon_phase_angle)

        # Determine progressive phase modifier
        moon_age = (moon_phase_angle / 360) * 29.53  # Convert phase angle to Moon's age (0-29.53 days)
        if moon_age <= 7.38:  # New Moon to First Quarter (Waxing)
            phase_modifier = -0.5 + (moon_age / 7.38) * 1.0
        elif moon_age <= 14.77:  # First Quarter to Full Moon (Waxing)
            phase_modifier = 0.5 + ((moon_age - 7.38) / 7.39) * 0.7
        elif moon_age <= 22.15:  # Full Moon to Last Quarter (Waning)
            phase_modifier = 1.2 - ((moon_age - 14.77) / 7.38) * 1.7
        else:  # Last Quarter to New Moon (Waning)
            phase_modifier = -0.5 - ((moon_age - 22.15) / 7.38) * 0.2

        # Determine phase description
        if moon_phase_angle < 1:
            phase = "New Moon"
        elif 89 <= moon_phase_angle <= 91:
            phase = "First Quarter"
        elif 179 <= moon_phase_angle <= 181:
            phase = "Full Moon"
        elif 269 <= moon_phase_angle <= 271:
            phase = "Last Quarter"
        else:
            phase = "Waxing" if moon_longitude > sun_longitude else "Waning"

        # Calculate declination using equatorial coordinates
        observer_time = ts.from_datetime(self.now_utc)
        moon_equatorial = ephemeris['earth'].at(observer_time).observe(ephemeris['moon']).apparent().radec()
        moon_declination = moon_equatorial[1].degrees  # Declination in degrees

        # Update Moon data with additional properties
        moon_data.update({
            "phase": str(phase),  # Ensure this is a string
            "phase_angle": float(moon_phase_angle),  # Ensure numeric types are floats
            "declination": float(moon_declination),  # Ensure numeric types are floats
            "is_out_of_bounds": bool(abs(moon_declination) > 23.44),  # Explicitly cast to bool
            "illumination_percentage": float(illumination_percentage),
            "phase_modifier": round(phase_modifier, 2),  # Include progressive phase modifier
        })

        return moon_data

   
    # -------------------------------------------------------------------------------
    # HOUSING WORK
    # -------------------------------------------------------------------------------

    def calculate_complete_chart(self):
        """
        Calculate complete chart data:
        1. Calculate planetary positions using Skyfield
        2. Calculate houses using Swiss Ephemeris
        3. Place planets in houses
        """
        try:
            # 1. First get all planetary positions (using existing Skyfield calculation)
            planet_positions = self.calculate_planetary_positions()
            
            # 2. Calculate house cusps using Swiss Ephemeris
            jd = swe.julday(
                self.now_utc.year,
                self.now_utc.month,
                self.now_utc.day,
                self.now_utc.hour + self.now_utc.minute / 60.0 + self.now_utc.second / 3600.0,
            )
            cusps, ascmc = swe.houses(jd, self.latitude, self.longitude, b'R')

            # 3. Create house structure with zodiacal info
            houses = {}
            for i in range(12):
                absolute_degree = round(cusps[i], 2)
                sign_index = int(absolute_degree // 30) % 12
                houses[i + 1] = {
                    "absolute_degree": absolute_degree,
                    "degree": round(absolute_degree % 30, 2),
                    "sign": ZODIAC_SIGNS[sign_index],
                    "planets": []  # Will hold planets that fall in this house
                }

            # 4. Place planets in houses
            for planet_name, planet_data in planet_positions.items():
                planet_degree = float(planet_data["longitude"])
                
                # Find which house the planet belongs in
                for house in range(1, 13):
                    next_house = 1 if house == 12 else house + 1
                    start_degree = houses[house]["absolute_degree"]
                    end_degree = houses[next_house]["absolute_degree"]

                    # Check if planet falls within house boundaries
                    if (end_degree < start_degree and 
                        (planet_degree >= start_degree or planet_degree < end_degree)) or \
                    (end_degree > start_degree and 
                        start_degree <= planet_degree < end_degree):
                        
                        # Add planet to house with all its calculated data
                        houses[house]["planets"].append({
                            "name": planet_name,
                            **planet_data  # Include all planetary data (position, retrograde, speed, etc.)
                        })
                        break

            # 5. Add important angles
            angles = {
                "ascendant": {
                    "absolute_degree": round(ascmc[0], 2),
                    "degree": round(ascmc[0] % 30, 2),
                    "sign": ZODIAC_SIGNS[int(ascmc[0] // 30) % 12]
                },
                "midheaven": {
                    "absolute_degree": round(ascmc[1], 2),
                    "degree": round(ascmc[1] % 30, 2),
                    "sign": ZODIAC_SIGNS[int(ascmc[1] // 30) % 12]
                },
                "descendant": {
                    "absolute_degree": round((ascmc[0] + 180) % 360, 2),
                    "degree": round((ascmc[0] + 180) % 30, 2),
                    "sign": ZODIAC_SIGNS[int((ascmc[0] + 180) // 30) % 12]
                },
                "ic": {
                    "absolute_degree": round((ascmc[1] + 180) % 360, 2),
                    "degree": round((ascmc[1] + 180) % 30, 2),
                    "sign": ZODIAC_SIGNS[int((ascmc[1] + 180) // 30) % 12]
                }
            }

            return {
                "houses": houses,
                "angles": angles,
                "planets": planet_positions  # Include full planetary data separately as well
            }

        except Exception as e:
            print(f"Error calculating chart: {str(e)}")
            return {"error": f"Chart calculation failed: {str(e)}"}



    # -------------------------------------------------------------------------------
    # DATABASE QUERY FORMAT NEO4J QUERY
    # -------------------------------------------------------------------------------

    def format_hour_name(self, hour_index):
        """
        Format hour name for Neo4j query.
        """
        day_segment = 'Day' if self.sunrise_local <= self.now_local <= self.sunset_local else 'Night'
        weekday = self.now_local.strftime('%A')
        return f"Hour_{ORDINAL_NAMES[hour_index]}_Of_{day_segment}_{weekday}"


    # -------------------------------------------------------------------------------
    # DATABASE QUERY CURRENT MAGIC HOUR
    # -------------------------------------------------------------------------------

    def fetch_hour_data(self, hour_name, planetary_positions):
        """
        Fetch and process Neo4j data.
        """
        with neo4j_driver.session() as session:
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
                        "planetary_positions": planetary_positions
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
                
            return simplified




geolocate_bp = Blueprint('geolocate', __name__)

@geolocate_bp.route('/api/geolocation_ephemeris', methods=['POST'])
def handle_geolocation_and_ephemeris():
    """Handle geolocation data and calculate ephemeris."""
    
    request_id = uuid.uuid4()
    print(f"DEBUG: Incoming request ID: {request_id}")
    
    try:
        data = request.json
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        print("DEBUG: Incoming data:", data)
        
        if latitude is None or longitude is None:
            return jsonify({"error": "Missing latitude or longitude"}), 400
        
        # Ensure latitude and longitude are floats
        if not isinstance(latitude, (float, int)) or not isinstance(longitude, (float, int)):
            raise ValueError(f"Invalid latitude or longitude: {latitude}, {longitude}")
            
        # Initialize calculator
        calculator = EphemerisCalculator(latitude, longitude)
        
        # Get all calculations
        hour_index, ruling_planet = calculator.calculate_planetary_hour() # Ruler of the current hour
        print(f"DEBUG: Ruling Planet: {ruling_planet}, Hour Index: {hour_index}")

        day_ruling_planet = DAY_RULERS[calculator.now_local.weekday()]  # Ruler of the current day
        print(f"DEBUG: Day Ruling Planet: {day_ruling_planet}")
        
        planetary_positions = calculator.calculate_planetary_positions()
        print("DEBUG: Planetary positions:", planetary_positions)
        
        # Calculate distances and append to planetary_positions
        planetary_distances = calculator.calculate_planetary_distances()
        for planet, distance in planetary_distances.items():
            if planet in planetary_positions:
                planetary_positions[planet]["distance_au"] = distance

        # Calculate combustion / cazimi and append to planetary positions
        combustion_cazimi = calculator.calculate_combustion_and_cazimi()
        for planet, status in combustion_cazimi.items():
            planetary_positions[planet].update(status)

        # Calculate Moon-specific properties and append to planetary positions
        moon_data = calculator.calculate_moon_properties(planetary_positions)
        if "Moon" in planetary_positions:
            planetary_positions["Moon"].update(moon_data)
        else:
            planetary_positions["Moon"] = moon_data

        # Calculate chart including key aspects
        chart_data = calculator.calculate_complete_chart()
        print("DEBUG: Chart Data:", chart_data)
        aspects = calculator.calculate_aspects()
        print("DEBUG: Aspects:", aspects)
        
        # Get Neo4j data
        hour_name = calculator.format_hour_name(hour_index)
        neo4j_data = calculator.fetch_hour_data(hour_name, planetary_positions)
        print("DEBUG: Neo4j data:", neo4j_data)
        
        # Bounce data to be used in heatmap route
        heatmap_data = HeatmapCalculator.calculate_heatmap_properties(
            planetary_positions=planetary_positions,
            ruling_planet=ruling_planet,
            day_ruling_planet=day_ruling_planet
        )
        print("DEBUG: Heatmap data:", heatmap_data)

        # Prepare Response
        response_data = {
            "latitude": latitude,
            "longitude": longitude,

            "current_time": calculator.now_local.strftime('%H:%M:%S'),
            "current_date": calculator.now_local.strftime('%Y-%m-%d'),
            "sunrise": calculator.sunrise_local.strftime('%H:%M:%S'),
            "sunset": calculator.sunset_local.strftime('%H:%M:%S'),
            "utc_time": calculator.now_utc.strftime('%H:%M:%S') if calculator.now_utc else "N/A",

            "current_planetary_hour": hour_index + 1 if hour_index is not None else "N/A",
            "ruling_planet": ruling_planet if ruling_planet else "N/A",
            "day_ruling_planet": day_ruling_planet if day_ruling_planet else "N/A",

            "planetary_positions": planetary_positions,
            "planetary_distances": planetary_distances,
            "combustion_cazimi": combustion_cazimi,
            "moon_data": moon_data,
            "aspects": aspects,
            
            "planetary_positions": chart_data["planets"],
            "houses": chart_data["houses"],
            "angles": chart_data["angles"],
            "zodiac_signs": ZODIAC_SIGNS,  

            "neo4j_data": neo4j_data,
            "heatmap_data": heatmap_data,
            
            "message": "Calculations completed successfully"
        }
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        print(f"Error in handler: {e}\n{traceback.format_exc()}")
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "trace": traceback.format_exc()
        }), 500
    


# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# HEATMAP CALCULATOR CLASS
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

class HeatmapCalculator:
    
    @staticmethod
    def calculate_dignity_modifier(planet, sign):
        """
        Determine the essential dignity of a planet based on its zodiac sign.
        """
        dignity = ESSENTIAL_DIGNITIES.get(planet, {})
        if sign == dignity.get('rulership'):
            return 1.5
        elif sign == dignity.get('exaltation'):
            return 1.25
        elif sign == dignity.get('detriment'):
            return 0.75
        elif sign == dignity.get('fall'):
            return 0.5
        else:
            return 1.0
     
    @staticmethod
    def calculate_moon_phase_modifier(phase_angle):
        """
        Calculate the Moon-specific phase modifier based on its phase angle.
        """
        if phase_angle is None:
            return {"phase_modifier": 0, "phase_angle": None}

        if phase_angle <= 90:  # New Moon to First Quarter (Waxing)
            phase_modifier = -0.7 + (phase_angle / 90) * 1.0
        elif phase_angle <= 180:  # First Quarter to Full Moon (Waxing)
            phase_modifier = 0.3 + ((phase_angle - 90) / 90) * 0.9
        elif phase_angle <= 270:  # Full Moon to Last Quarter (Waning)
            phase_modifier = 1.2 - ((phase_angle - 180) / 90) * 1.6
        else:  # Last Quarter to New Moon (Waning)
            phase_modifier = -0.4 - ((phase_angle - 270) / 90) * 0.3

        return {
            "phase_modifier": round(phase_modifier, 2),
            "phase_angle": round(phase_angle, 2),
        }
    

    @staticmethod
    def calculate_combustion_cazimi_modifier(is_cazimi, is_combust):
        """
        Determine the combustion or cazimi modifier based on precomputed status flags.
        """
        if is_cazimi:
            return {
                "combustion_modifier": 0.5,  # Bonus for cazimi
                "combustion_status": "Cazimi",
            }
        elif is_combust:
            return {
                "combustion_modifier": -1.8,  # Penalty for combustion
                "combustion_status": "Combust",
            }
        else:
            return {
                "combustion_modifier": 0,
                "combustion_status": "None",
            }

    
    @staticmethod
    def calculate_planet_intensity(
        planet_name,
        position,
        ruling_planet,
        day_ruling_planet
    ):
        """
        Calculate the intensity of a planet based on various factors.
        """
        # Proximity Intensity
        distance_au = position.get("distance_au", 1.0)
        intensity_proximity = 1 / distance_au
        intensity_proximity = min(intensity_proximity, 10)  # Cap proximity intensity

        # Visibility Factor (Altitude)
        altitude = position.get("altitude", 0)
        visibility_factor = (
            altitude / 90 if altitude >= 0 else max(altitude / 90 * 0.4, 0.1)
        )

        # Ruling Bonuses
        bonus = 0
        if planet_name == ruling_planet and planet_name == day_ruling_planet:
            bonus += 1.5  # Max bonus for ruling both hour and day
        elif planet_name == ruling_planet:
            bonus += 1.0  # Hour ruler bonus
        elif planet_name == day_ruling_planet:
            bonus += 0.5  # Day ruler bonus

        # Dignity Modifier
        sign = position.get("sign", "")
        dignity_modifier = HeatmapCalculator.calculate_dignity_modifier(planet_name, sign)

        # Combustion and Cazimi Effects
        angular_distance = position.get("angular_distance", None)
        combustion_modifier, combustion_status = HeatmapCalculator.calculate_combustion_cazimi_modifier(
            planet_name, angular_distance
        )

        # Moon-Specific Phase Modifier
        phase_modifier = 0
        if planet_name == "Moon":
            phase_angle = position.get("phase_angle", 0)
            phase_modifier = HeatmapCalculator.calculate_moon_phase_modifier(phase_angle)

        # Final Intensity Calculation
        intensity = (
            0.25 * intensity_proximity +
            0.35 * visibility_factor +
            0.2 * dignity_modifier +
            0.1 * bonus +
            0.1 * phase_modifier +
            combustion_modifier  # Include combustion/cazimi effects
        )
        intensity = max(round(intensity, 2), 0)  # Ensure non-negative

        return intensity, combustion_status
    

    @staticmethod
    def generate_gradient(heatmap_data):
        """
        Generate a CSS linear gradient from heatmap data.

        Args:
            heatmap_data (list): List of heatmap entries containing planet properties.

        Returns:
            str: A CSS linear gradient string.
        """
        gradient_stops = []

        for entry in heatmap_data:
            planet_color = entry.get("color", "#FFFFFF")
            intensity = entry.get("intensity", 0)  # Normalized intensity (0 to 1)
            azimuth = entry.get("azimuth", 0)  # Angle for the gradient

            # Normalize intensity to a percentage for gradient opacity
            opacity = min(max(intensity / 2, 0.1), 1.0)  # Scale intensity to 10% - 100%

            # Add a gradient stop
            gradient_stops.append(f"rgba({int(planet_color[1:3], 16)},"
                                f"{int(planet_color[3:5], 16)},"
                                f"{int(planet_color[5:7], 16)},"
                                f"{opacity}) {azimuth}deg")

        # Combine stops into a CSS linear gradient
        gradient_css = f"linear-gradient({', '.join(gradient_stops)})"
        return gradient_css

    

    @staticmethod
    def calculate_heatmap_properties(planetary_positions, ruling_planet, day_ruling_planet):
        """
        Process planetary positions to generate heatmap data, accessing fields as dictionaries.
        """
        heatmap_data = []

        for planet_name, position in planetary_positions.items():
            try:
                # Access fields as dictionary keys
                altitude = position.get("altitude", 0)  # Default to 0 if not found
                azimuth = position.get("azimuth", 0)
                distance_au = position.get("distance_au", 1.0)
                is_retrograde = position.get("is_retrograde", False)
                is_stationary = position.get("is_stationary", False)
                daily_motion = position.get("daily_motion", 0)
                longitude = position.get("longitude", 0)
                sign = position.get("sign", "")
                phase_angle = position.get("phase_angle", 0)

                is_cazimi = position.get("is_cazimi", False)
                is_combust = position.get("is_combust", False)

                is_out_of_bounds = position.get("is_out_of_bounds", False)

                # Determine if the current planet is ruling or day ruling
                is_ruling_planet = planet_name.lower() == ruling_planet.lower()
                is_day_ruling_planet = planet_name.lower() == day_ruling_planet.lower()

                combustion_data = HeatmapCalculator.calculate_combustion_cazimi_modifier(
                is_cazimi, is_combust
                )

                # Call moon's phase modifier function
                phase_modifier = 0
                moon_warning = None
                if planet_name == "Moon":
                    # Phase modifier
                    moon_phase_data = HeatmapCalculator.calculate_moon_phase_modifier(phase_angle)
                    phase_modifier = moon_phase_data["phase_modifier"]

                    # Add Moon-specific warnings
                    moon_warning = []
                    if is_combust:
                        moon_warning.append("The Moon is combust. Avoid critical actions.")
                    if is_out_of_bounds:
                        moon_warning.append("The Moon is out of bounds. Exercise caution in decisions.")


                # Calculate intensity (comment out cazimi/combustion for now)
                intensity = 0  # Placeholder intensity calculation to ensure functionality

                # Create a heatmap entry
                heatmap_entry = {
                    "planet": planet_name,
                    "altitude": round(altitude, 2),
                    "azimuth": round(azimuth, 2),
                    "distance_au": round(distance_au, 3),
                    "is_retrograde": is_retrograde,
                    "is_stationary": is_stationary,
                    "daily_motion": daily_motion,
                    "longitude": round(longitude, 2),
                    "sign": sign,
                    "is_ruling_planet": is_ruling_planet,
                    "is_day_ruling_planet": is_day_ruling_planet,
                    "is_cazimi": is_cazimi,
                    "is_combust": is_combust,
                    "combustion_modifier": combustion_data["combustion_modifier"],
                    "combustion_status": combustion_data["combustion_status"],
                    "phase_angle": round(phase_angle, 2) if planet_name == "Moon" else None,
                    "is_out_of_bounds": is_out_of_bounds if planet_name == "Moon" else None,
                    "phase_modifier": phase_modifier,
                    "intensity": intensity,  
                    "color": PLANETARY_COLORS.get(planet_name, "#FFFFFF"),
                    "warnings": moon_warning if planet_name == "Moon" else None,  # Add warnings for Moon
                }

                heatmap_data.append(heatmap_entry)

            except Exception as e:
                print(f"Error processing {planet_name}: {e}")

        return heatmap_data



   
    # def calculate_heatmap_properties(planetary_positions, ruling_planet, day_ruling_planet):
    #     """
    #     Generate heatmap data using pre-calculated planetary positions and dynamic bonuses,
    #     with detailed logging for each calculation step.
    #     """
    #     heatmap_data = []

    #     for planet_name, position in planetary_positions.items():
            
    #         try:
    #             # Initialize calculation log
    #             log = {}

    #             # Proximity Intensity: Use angular distance if available
    #             distance_au = position.get('distance_au', 1.0)
    #             intensity_proximity = 1 / distance_au
    #             if planet_name == "Moon":
    #                 intensity_proximity = min(intensity_proximity * 0.1, 5)  # Reduce and cap Moon's proximity weight
    #             else:
    #                 intensity_proximity = min(intensity_proximity, 10)  # Cap proximity intensity for all planets
    #             log["intensity_proximity"] = round(intensity_proximity, 2)

    #             # Visibility Factor: Based on altitude
    #             altitude = position.get('altitude', 0)
    #             visibility_factor = (
    #                 altitude / 90 if altitude >= 0
    #                 else max(altitude / 90 * 0.4, 0.1)  # Lower negative altitude scaling for planets below the horizon
    #             )
    #             log["visibility_factor"] = round(visibility_factor, 2)

    #             # Bonuses for Ruling Planets
    #             bonus = 0
    #             if planet_name == ruling_planet and planet_name == day_ruling_planet:
    #                 bonus += 1.5  # Max potency for planets ruling both day and hour
    #             elif planet_name == ruling_planet:
    #                 bonus += 1.0  # Significant bonus for ruling the hour
    #             elif planet_name == day_ruling_planet:
    #                 bonus += 0.5  # Smaller bonus for ruling the day
    #             log["bonus"] = round(bonus, 2)

    #             # Angular Distance Modifiers
    #             angular_distance = position.get('angular_distance', None)
    #             if angular_distance is not None:
    #                 if 0 <= angular_distance <= 8.5:  # Cazimi
    #                     bonus += 0.5
    #                     log["angular_distance_effect"] = "Cazimi (+0.5 bonus)"
    #                 elif 8.5 < angular_distance <= 17.0:  # Combustion
    #                     bonus -= 0.8
    #                     log["angular_distance_effect"] = "Combustion (-0.8 penalty)"
    #                     if planet_name == "Moon":
    #                         position["warning"] = "The Moon is combust. Avoid critical actions."
    #             log["angular_distance"] = angular_distance

    #             # Dignity Modifier
    #             sign = position.get('sign', '')
    #             dignity_modifier = HeatmapCalculator.calculate_dignity_modifier(planet_name, sign)
    #             log["dignity_modifier"] = round(dignity_modifier, 2)

    #             # Moon-Specific Phase Modifier
    #             phase_modifier = 0
    #             if planet_name == "Moon":
    #                 phase_angle = position.get("phase_angle", 0)
    #                 if phase_angle <= 90:  # New Moon to First Quarter (Waxing)
    #                     phase_modifier = -0.7 + (phase_angle / 90) * 1.0
    #                 elif phase_angle <= 180:  # First Quarter to Full Moon (Waxing)
    #                     phase_modifier = 0.3 + ((phase_angle - 90) / 90) * 0.9
    #                 elif phase_angle <= 270:  # Full Moon to Last Quarter (Waning)
    #                     phase_modifier = 1.2 - ((phase_angle - 180) / 90) * 1.6
    #                 else:  # Last Quarter to New Moon (Waning)
    #                     phase_modifier = -0.4 - ((phase_angle - 270) / 90) * 0.3
    #                 log["phase_angle"] = round(phase_angle, 2)
    #                 log["phase_modifier"] = round(phase_modifier, 2)

    #             # Final Intensity Calculation
    #             intensity = (
    #                 0.25 * intensity_proximity +  # Slightly higher weight for proximity
    #                 0.35 * visibility_factor +    # Visibility remains prominent
    #                 0.25 * dignity_modifier +     # Dignity contributes significantly
    #                 bonus +                       # Ruling planet bonuses
    #                 phase_modifier                # Moon-specific phase effects
    #             )
    #             intensity = max(round(intensity, 2), 0)  # Ensure intensity is non-negative
    #             log["final_intensity"] = intensity

    #             # Append Data to Heatmap
    #             heatmap_entry = {
    #                 "planet": planet_name,
    #                 "azimuth": round(position.get('azimuth', 0), 2),
    #                 "altitude": round(altitude, 2),
    #                 "intensity": intensity,
    #                 "color": PLANETARY_COLORS.get(planet_name, "#FFFFFF"),
    #                 "is_retrograde": position.get(is_retrograde),
    #                 "distance_au": distance_au, # Add this line
    #                 "log": log  # Include detailed calculation log
    #             }

    #             # Add warning if applicable
    #             if "warning" in position:
    #                 heatmap_entry["warning"] = position["warning"]

    #             heatmap_data.append(heatmap_entry)

    #         except Exception as e:
    #             print(f"Error processing {planet_name}: {e}")

    #     return heatmap_data
    
