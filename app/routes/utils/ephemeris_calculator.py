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

from app.routes.constants import DAY_RULERS, ZODIAC_SIGNS, EXTENDED_PLANETARY_ORDER, EXTENDED_SKYFIELD_IDS, DEFAULT_ASPECT_CONFIG
from app.routes.constants import ephemeris, ts


class EphemerisCalculator:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        self.observer = wgs84.latlon(latitude, longitude)

        # Determine timezone
        tz_finder = TimezoneFinder()
        self.timezone_name = tz_finder.timezone_at(lat=latitude, lng=longitude)
        if not self.timezone_name:
            raise ValueError("Could not determine timezone for the given location.")
        self.timezone = pytz_timezone(self.timezone_name)

        # Initialize times
        self.now_utc = datetime.now(dt_timezone.utc)
        self.now_local = self.now_utc.astimezone(self.timezone)
        self.sunrise_local, self.sunset_local = self._calculate_sun_times()
  
        
    def _convert_to_serializable(self, data):
        """
        Recursively convert data to JSON-serializable types.

        Args:
            data (any): The data to convert.

        Returns:
            any: JSON-serializable data.
        """
        if isinstance(data, dict):
            return {key: self._convert_to_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_serializable(item) for item in data]
        elif isinstance(data, (int, float, str, type(None))):
            return data
        elif hasattr(data, "isoformat"):  # Handle datetime objects
            return data.isoformat()
        elif isinstance(data, (np.float64, np.int64)):  # Handle NumPy data types
            return data.item()
        else:
            return str(data)  # Fallback: Convert unknown types to string
        
    
    def generate_ephemeris_dataset(self):
        """
        Generate a unified dataset that aggregates all planetary data:
        - Planetary positions (longitude, altitude, azimuth, retrograde, etc.)
        - Planetary distances (AU)
        - Combustion and cazimi status
        - Aspects between planets
        - Moon-specific properties (illumination, phase, declination, etc.)
        - Additional information: current_date, current_time, etc.

        Returns:
            dict: A comprehensive dataset of planetary and additional data.
        """
        # Step 1: Calculate planetary positions
        planetary_positions = self.calculate_planetary_positions()

        # Step 2: Add distances to planetary positions
        planetary_distances = self.calculate_planetary_distances()
        for planet, distance in planetary_distances.items():
            if planet in planetary_positions:
                if isinstance(distance, dict) and "error" in distance:
                    planetary_positions[planet]["distance_error"] = distance["error"]
                    planetary_positions[planet]["distance_au"] = None
                else:
                    planetary_positions[planet]["distance_au"] = float(distance)

        # Step 3: Add combustion and cazimi status
        combustion_cazimi = self.calculate_combustion_and_cazimi()
        for planet, data in combustion_cazimi.items():
            if planet in planetary_positions:
                planetary_positions[planet].update(data)

        # Step 4: Add Moon-specific properties
        moon_data = self.calculate_moon_properties(
            positions=planetary_positions, precomputed_results=combustion_cazimi
        )
        planetary_positions["Moon"].update(moon_data)
        print(f"DEBUG: Updated Moon Data: {planetary_positions['Moon']}")

        # Step 5: Calculate aspects between planets
        aspects = self.calculate_aspects()
        
        # Step 6: Calculate complete chart
        chart_data = self.calculate_complete_chart()

        # Step 7: Add additional information
        current_date = self.now_local.strftime('%Y-%m-%d')
        current_time = self.now_local.strftime('%H:%M:%S')
        utc_time = self.now_utc.strftime('%H:%M:%S')
        sunrise = self.sunrise_local.strftime('%H:%M:%S')
        sunset = self.sunset_local.strftime('%H:%M:%S')
        hour_index = self.calculate_planetary_hour()
        day_ruling_planet = DAY_RULERS[self.now_local.weekday()]

        # Step 8: Combine all data into a unified dataset
        ephemeris_dataset = {
            "planets": self._convert_to_serializable(planetary_positions),  # Centralized planetary data
            "chart": {
                "houses": self._convert_to_serializable(chart_data["houses"]),  
                "angles": self._convert_to_serializable(chart_data["angles"]),
                "aspects": self._convert_to_serializable(aspects),
            },
            "additional_info": {
                "current_date": current_date,
                "current_time": current_time,
                "utc_time": utc_time,
                "current_planetary_hour": hour_index,
                "day_ruling_planet": day_ruling_planet,
                "sunrise": sunrise,
                "sunset": sunset,
            },
        }

        return ephemeris_dataset




    def _calculate_sun_times(self):
        """
        Calculate sunrise and sunset times for the observer's location.

        Returns:
            tuple: A tuple containing sunrise_local and sunset_local (timezone-aware datetime).
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

    
 
   
    def calculate_planetary_hour(self):
        """
        Calculate the current planetary hour index.
        
        Returns:
            int: The hour number (1 to 12 for day hours, -1 to -12 for night hours)
        """
        if not hasattr(self, 'sunrise_local') or not hasattr(self, 'sunset_local'):
            raise ValueError("Sunrise and sunset times must be calculated before determining the planetary hour.")

        is_daytime = self.sunrise_local <= self.now_local <= self.sunset_local

        if is_daytime:
            # Daytime: Calculate positive hour index (1 to 12)
            duration = (self.sunset_local - self.sunrise_local).total_seconds() / 12
            time_since_sunrise = (self.now_local - self.sunrise_local).total_seconds()
            hour_index = int(time_since_sunrise // duration) + 1
            return min(12, max(1, hour_index))  # Ensure between 1 and 12
        else:
            # Nighttime: Calculate negative hour index (-1 to -12)
            next_sunrise_local = self.sunrise_local + timedelta(days=1)
            duration = (next_sunrise_local - self.sunset_local).total_seconds() / 12
            time_since_sunset = (self.now_local - self.sunset_local).total_seconds()
            hour_index = -(int(time_since_sunset // duration) + 1)
            return max(-12, min(-1, hour_index))  # Ensure between -12 and -1
    
    
    def get_day_ruler(self):
        """
        Determine the day ruler based on the current day of the week.

        Returns:
            str: The ruling planet of the current day.
        """
        day_index = self.now_local.weekday()
        return DAY_RULERS[day_index]


    def calculate_planetary_positions(self):
        """
        Calculate positions for all planets using constants from constants.py.
        """
        positions = {}
        observer_time = ts.from_datetime(self.now_utc)
        observer_time_tomorrow = ts.from_datetime(self.now_utc + timedelta(days=1))

        earth = ephemeris['earth']
        topos = earth + self.observer

        for planet_name in EXTENDED_PLANETARY_ORDER:
            try:
                planet = ephemeris[EXTENDED_SKYFIELD_IDS[planet_name]]

                # Calculate ecliptic longitude and daily motion
                longitude, daily_motion, is_retrograde, is_stationary = self._calculate_longitude_and_motion(
                    topos, observer_time, observer_time_tomorrow, planet
                )

                # Normalize position to zodiac
                sign_index = int(longitude // 30)
                sign_degree = longitude % 30

                # Calculate altitude and azimuth
                alt, az = self._calculate_alt_az(topos, observer_time, planet)

                # Build position data
                positions[planet_name] = {
                    "longitude": round(longitude, 2),
                    "sign": ZODIAC_SIGNS[sign_index],
                    "degree": round(sign_degree, 2),
                    "is_retrograde": is_retrograde,
                    "is_stationary": is_stationary,
                    "daily_motion": round(daily_motion, 4),
                    "altitude": round(alt, 2),
                    "azimuth": round(az, 2),
                }

                # Add Moon-specific distance (AU and KM)
                if planet_name == 'Moon':
                    distance_au = topos.at(observer_time).observe(planet).distance().au
                    positions['Moon']["distance_au"] = round(distance_au, 6)
                    positions['Moon']["distance_km"] = round(distance_au * 149597870.7, 2)  # AU to KM

            except Exception as e:
                print(f"Error calculating {planet_name}: {e}")
                positions[planet_name] = self._fallback_position_data(e)

        self.planetary_positions = positions  # Assign to instance
        return positions

    def _calculate_longitude_and_motion(self, topos, observer_time, observer_time_tomorrow, planet):
        """
        Calculate ecliptic longitude, daily motion, retrograde, and stationary status.
        """
        astrometric = topos.at(observer_time).observe(planet)
        ecliptic_pos = astrometric.ecliptic_latlon()
        longitude = float(ecliptic_pos[1].degrees)

        # Calculate tomorrow's position for motion
        astrometric_tomorrow = topos.at(observer_time_tomorrow).observe(planet)
        ecliptic_pos_tomorrow = astrometric_tomorrow.ecliptic_latlon()
        longitude_tomorrow = float(ecliptic_pos_tomorrow[1].degrees)

        # Calculate daily motion
        daily_motion = longitude_tomorrow - longitude
        if daily_motion > 180:
            daily_motion -= 360
        elif daily_motion < -180:
            daily_motion += 360

        # Normalize longitude
        longitude = longitude % 360
        if longitude < 0:
            longitude += 360

        # Check retrograde and stationary
        is_retrograde = daily_motion < 0
        is_stationary = abs(daily_motion) < 0.01  # Threshold for stationary

        return longitude, daily_motion, is_retrograde, is_stationary

    def _calculate_alt_az(self, topos, observer_time, planet):
        """
        Calculate altitude and azimuth of a planet.
        """
        astrometric = topos.at(observer_time).observe(planet)
        alt, az, _ = astrometric.apparent().altaz()
        return alt.degrees, az.degrees

    def _fallback_position_data(self, error):
        """
        Provide fallback data for planets that fail calculations.
        """
        return {
            "longitude": 0,
            "sign": "Unknown",
            "degree": 0,
            "is_retrograde": False,
            "is_stationary": False,
            "daily_motion": 0.0,
            "altitude": 0.0,
            "azimuth": 0.0,
            "error": f"Calculation failed: {error}"
        }



    def calculate_planetary_distances(self):
        """
        Calculate the distance of each planet (including outer planets) from Earth using Skyfield.

        Returns:
            dict: A dictionary with planet names as keys and their distances (in AU) as values.
                If a planet's distance cannot be calculated, an error message is included.
        """
        observer_time = ts.from_datetime(self.now_utc)  # Use the current UTC time
        distances = {}

        earth = ephemeris['earth']

        for planet_name, skyfield_id in EXTENDED_SKYFIELD_IDS.items():  # Use extended IDs from constants
            try:
                planet_obj = ephemeris[skyfield_id]
                # Calculate distance from Earth
                distance = earth.at(observer_time).observe(planet_obj).distance().au
                distances[planet_name] = round(distance, 6)  # Round to 6 decimal places for precision
            except Exception as e:
                error_message = f"Failed to calculate distance for {planet_name}: {str(e)}"
                print(error_message)  # Log the error
                distances[planet_name] = {"error": error_message}

        return distances
    
    
    
    def calculate_combustion_and_cazimi(self):
        """
        Calculate combustion and cazimi for planets relative to the Sun.

        Combustion:
            A planet is considered combust if its angular distance from the Sun is ≤ 8.5°.

        Cazimi:
            A planet is considered cazimi if its angular distance from the Sun is ≤ 0.283°.

        Returns:
            dict: A dictionary where each planet (excluding the Sun) is mapped to its combustion
                and cazimi status, including angular distance from the Sun.

        Raises:
            ValueError: If the Sun's position is missing or cannot be calculated.
        """
        # Ensure planetary positions are precomputed
        if not hasattr(self, 'planetary_positions'):
            self.planetary_positions = self.calculate_planetary_positions()

        # Retrieve Sun's longitude
        sun_longitude = self.planetary_positions.get("Sun", {}).get("longitude")
        if sun_longitude is None:
            raise ValueError("Sun's position is required for combustion and cazimi calculations.")

        results = {}

        for planet, data in self.planetary_positions.items():
            if planet == "Sun":  # Skip the Sun itself
                continue

            # Use precomputed longitude for each planet
            planet_longitude = data["longitude"]
            angular_distance = abs(planet_longitude - sun_longitude)

            # Normalize angular distance to ensure it doesn't exceed 180°
            angular_distance = angular_distance if angular_distance <= 180 else 360 - angular_distance

            # Determine combustion and cazimi
            is_combust = angular_distance <= 8.5
            is_cazimi = angular_distance <= 0.283

            # Placeholder for out-of-bounds calculation (to be implemented)
            is_out_of_bounds = self._calculate_out_of_bounds(data)

            results[planet] = {
                "is_combust": is_combust,
                "is_cazimi": is_cazimi,
                "angular_distance": round(angular_distance, 2),
                "is_out_of_bounds": is_out_of_bounds
            }

        return results

    def _calculate_out_of_bounds(self, data):
        """
        Placeholder method for calculating out-of-bounds status for planets.

        Args:
            data (dict): The precomputed planetary data, including latitude and declination.

        Returns:
            bool: True if the planet is out of bounds, False otherwise.
        """
        # TODO: Implement actual out-of-bounds logic based on declination.
        return False



    def calculate_aspects(self, aspect_config=None):
        """
        Calculate aspects between planets based on their longitudes.

        Args:
            aspect_config (dict, optional): Aspect angles and their allowable orbs.
                Defaults to:
                    {
                        "Conjunction": {"angle": 0, "orb": 8},
                        "Opposition": {"angle": 180, "orb": 8},
                        "Square": {"angle": 90, "orb": 7},
                        "Trine": {"angle": 120, "orb": 7},
                        "Sextile": {"angle": 60, "orb": 6},
                    }

        Returns:
            list: List of aspects, including the two planets involved and their relationship.
        """
        # Use precomputed planetary positions
        if not hasattr(self, 'planetary_positions'):
            self.planetary_positions = self.calculate_planetary_positions()

        # Use default aspect configuration if none is provided
        if aspect_config is None:
            aspect_config = DEFAULT_ASPECT_CONFIG

        aspects = []
        planets = list(self.planetary_positions.keys())  # Get all planet names

        # Iterate over all unique pairs of planets
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1, planet2 = planets[i], planets[j]
                pos1, pos2 = self.planetary_positions[planet1]["longitude"], self.planetary_positions[planet2]["longitude"]

                # Calculate angular distance
                angular_distance = self._calculate_angular_distance(pos1, pos2)

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

    def _calculate_angular_distance(self, pos1, pos2):
        """
        Calculate the angular distance between two positions.

        Args:
            pos1 (float): Longitude of the first planet.
            pos2 (float): Longitude of the second planet.

        Returns:
            float: Normalized angular distance (0° to 180°).
        """
        angular_distance = abs(pos1 - pos2)
        return angular_distance if angular_distance <= 180 else 360 - angular_distance
    
    
    def calculate_moon_properties(self, positions=None, precomputed_results=None):
        """
        Calculate detailed properties of the Moon, reusing precomputed data if available.

        Args:
            positions (dict, optional): Precomputed planetary positions. If not provided,
                                        positions are computed internally.
            precomputed_results (dict, optional): Precomputed data such as combustion/cazimi.

        Returns:
            dict: Detailed Moon properties (phase, distance, declination, etc.).
        """
        if positions is None:
            positions = self.calculate_planetary_positions()

        moon_data = positions.get("Moon")
        if not moon_data:
            raise ValueError("Moon's position is not available in planetary positions.")

        if precomputed_results and "Moon" in precomputed_results:
            moon_data.update(precomputed_results["Moon"])

        sun_longitude = positions.get("Sun", {}).get("longitude")
        if not sun_longitude:
            raise ValueError("Sun's position is required for Moon phase calculations.")

        moon_longitude = moon_data["longitude"]
        moon_phase_angle = abs(moon_longitude - sun_longitude)
        if moon_phase_angle > 180:
            moon_phase_angle = 360 - moon_phase_angle

        illumination_percentage = self.calculate_moon_illumination(moon_phase_angle)
        moon_age = (moon_phase_angle / 360) * 29.53
        phase_modifier = self._calculate_phase_modifier(moon_age)
        phase = self._determine_moon_phase_description(moon_phase_angle, moon_longitude, sun_longitude)

        observer_time = ts.from_datetime(self.now_utc)
        moon_equatorial = ephemeris['earth'].at(observer_time).observe(ephemeris['moon']).apparent().radec()
        moon_declination = moon_equatorial[1].degrees

        moon_data.update({
            "phase": phase,
            "phase_angle": moon_phase_angle,
            "declination": moon_declination,
            "is_out_of_bounds": abs(moon_declination) > 23.44,
            "illumination_percentage": illumination_percentage,
            "phase_modifier": round(phase_modifier, 2),
        })

        return moon_data

    
    def calculate_moon_illumination(self, phase_angle):
        """
        Calculate the percentage of the Moon's surface that is illuminated.

        Args:
            phase_angle (float): The phase angle between the Moon and Sun in degrees.

        Returns:
            float: The percentage of the Moon's surface that is illuminated.
        """
        phase_angle_radians = math.radians(phase_angle)
        illumination_percentage = (1 + math.cos(phase_angle_radians)) / 2 * 100
        return round(illumination_percentage, 2)

    
    def _determine_moon_phase_description(self, phase_angle, moon_longitude, sun_longitude):
        """
        Determine the phase description of the Moon.

        Args:
            phase_angle (float): The angle between the Moon and the Sun.
            moon_longitude (float): The longitude of the Moon.
            sun_longitude (float): The longitude of the Sun.

        Returns:
            str: The Moon's phase description.
        """
        if phase_angle < 1:
            return "New Moon"
        elif 89 <= phase_angle <= 91:
            return "First Quarter"
        elif 179 <= phase_angle <= 181:
            return "Full Moon"
        elif 269 <= phase_angle <= 271:
            return "Last Quarter"
        return "Waxing" if moon_longitude > sun_longitude else "Waning"


    def _calculate_phase_modifier(self, moon_age):
        """
        Determine the Moon's phase modifier based on its age.

        Args:
            moon_age (float): The age of the Moon in days (0-29.53).

        Returns:
            float: The phase modifier.
        """
        if moon_age <= 7.38:
            return -0.5 + (moon_age / 7.38) * 1.0
        elif moon_age <= 14.77:
            return 0.5 + ((moon_age - 7.38) / 7.39) * 0.7
        elif moon_age <= 22.15:
            return 1.2 - ((moon_age - 14.77) / 7.38) * 1.7
        return -0.5 - ((moon_age - 22.15) / 7.38) * 0.2
    
    
    def get_zodiac_sign(self, degree):
        """
        Get zodiac sign accounting for boundary conditions.
        
        Args:
            degree (float): Absolute degree position (0-360)
        Returns:
            str: Zodiac sign name
        """
        # Handle edge case of 360 degrees
        if degree >= 360:
            degree -= 360
            
        # Add a tiny offset to handle boundary cases
        epsilon = 0.001
        adjusted_degree = degree + epsilon
        
        # Print debug info
        sign_index = int(adjusted_degree // 30) % 12
        print(f"DEBUG: degree={degree}, adjusted={adjusted_degree}, index={sign_index}, sign={ZODIAC_SIGNS[sign_index]}")
        
        return ZODIAC_SIGNS[sign_index]
        
    
    def calculate_complete_chart(self):
        """
        Calculate the complete astrological chart, including:
        1. Planetary positions using Skyfield
        2. House cusps and zodiac signs using Swiss Ephemeris
        3. Assign planets to their respective houses
        4. Determine important chart angles (Ascendant, MC, etc.)
        """
        try:
            # 1. Calculate planetary positions
            planetary_positions = self.calculate_planetary_positions()

            # 2. Calculate house cusps using Swiss Ephemeris
            jd = swe.julday(
                self.now_utc.year,
                self.now_utc.month,
                self.now_utc.day,
                self.now_utc.hour + self.now_utc.minute / 60.0 + self.now_utc.second / 3600.0,
            )
            cusps, ascmc = swe.houses(jd, self.latitude, self.longitude, b'R')
            print(f"DEBUG: Raw House cusps: {cusps}")
            print(f"DEBUG: Raw angles (ascmc): {ascmc}")
            

            # 3. Define house structure
            houses = {}
            for i in range(12):
                current_cusp = round(cusps[i], 2)
                
                houses[i + 1] = {
                    "absolute_degree": current_cusp,
                    "degree": round(current_cusp % 30, 2),
                    "sign": self.get_zodiac_sign(current_cusp),
                    "planets": []
                }
                print(f"DEBUG: House {i+1}: absolute_degree={current_cusp}, "
                    f"sign={self.get_zodiac_sign(current_cusp)}")
                
                
                
            # 4. Assign planets to houses
            for planet_name, planet_data in planetary_positions.items():
                planet_degree = planet_data["longitude"]
                for house in range(1, 13):
                    next_house = 1 if house == 12 else house + 1
                    start_degree = houses[house]["absolute_degree"]
                    end_degree = houses[next_house]["absolute_degree"]

                    # Handle wrap-around for houses crossing 0° Aries
                    if (end_degree < start_degree and 
                        (planet_degree >= start_degree or planet_degree < end_degree)) or \
                    (end_degree > start_degree and 
                        start_degree <= planet_degree < end_degree):
                        houses[house]["planets"].append({
                            "name": planet_name,
                            #**planet_data  # Include all planetary data
                        })
                        break

            # 5. Calculate chart angles (ASC, MC, DSC, IC)
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

            # Return the complete chart data
            return {
                "houses": houses,
                "angles": angles,
                "planets": planetary_positions  # Include full planetary data separately
            }

        except Exception as e:
            print(f"Error calculating chart: {str(e)}")
            return {"error": f"Chart calculation failed: {str(e)}"}




        