from app.routes.constants import PLANETARY_COLORS, ESSENTIAL_DIGNITIES, PLANET_DIAMETERS
import math
from typing import List, Dict


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
    def calculate_moon_phase_modifier(planets_data):
        """
        Calculate the Moon-specific phase modifier based on its phase angle within planets data.

        Args:
            planets_data (dict): Dictionary containing data for all planets, including the Moon.

        Returns:
            dict: A dictionary with the phase modifier and the phase angle for the Moon.
        """
        # Extract the Moon's data
        moon_data = planets_data.get("Moon", {})
        phase_angle = moon_data.get("phase_angle")

        if phase_angle is None:
            return {"phase_modifier": 0, "phase_angle": None}

        # Calculate phase modifier based on the angle
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
    def calculate_combustion_cazimi_modifier(planet_data):
        """
        Calculate the combustion or cazimi modifier for a planet based on its data.

        Args:
            planet_data (dict): Dictionary containing data for a specific planet,
                                including 'is_cazimi' and 'is_combust' flags.

        Returns:
            dict: A dictionary with the combustion modifier and combustion status.
        """
        is_cazimi = planet_data.get("is_cazimi", False)
        is_combust = planet_data.get("is_combust", False)

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
    def normalize_planet_size(planet_name: str, planets_data: dict) -> float:
        """Calculate normalized size based primarily on distance, with minimal physical diameter influence."""
        # Get all distances and current distance
        distances = [position.get("distance_au", 1.0) for position in planets_data.values()]
        min_distance = min(distances)
        max_distance = max(distances)
        current_distance = planets_data[planet_name].get("distance_au", 1.0)
        
        # Constants - reduced overall sizes and range
        max_distance_size = 35  # Reduced from 50
        min_distance_size = 5
        max_diameter_size = 15  # Reduced from 25
        min_diameter_size = 5

        # Calculate distance size with logarithmic scaling
        log_distance = math.log10(current_distance + 1)
        min_log = math.log10(min_distance + 1)
        max_log = math.log10(max_distance + 1)
        
        distance_size = (
            ((max_log - log_distance) / (max_log - min_log)) *
            (max_distance_size - min_distance_size) +
            min_distance_size
        )

        # Physical size normalization - but with much less influence
        diameter = PLANET_DIAMETERS[planet_name]
        max_diameter = max(PLANET_DIAMETERS.values())
        min_diameter = min(PLANET_DIAMETERS.values())
        
        diameter_size = (
            ((diameter - min_diameter) / (max_diameter - min_diameter)) *
            (max_diameter_size - min_diameter_size) +
            min_diameter_size
        )

        # Combined size with much stronger weight on distance
        return 0.85 * distance_size + 0.15 * diameter_size  # Changed from 0.6/0.4 split
    
    



    @staticmethod
    def calculate_planet_intensity(
        planet_name,
        position,
        hour_ruler,
        day_ruling_planet
    ):
        """
        Calculate the intensity of a planet based on various factors,
        with debug logs at each step.
        
        Args:
            planet_name (str): Name of the planet being evaluated.
            position (dict): Data for the planet, including altitude, sign, distance, etc.
            hour_ruler (str): Planet ruling the current hour.
            day_ruling_planet (str): Planet ruling the current day.

        Returns:
            tuple: (intensity, combustion_status)
        """
        # print(f"[LOG] --- Calculating intensity for {planet_name} ---")

        # 1) PROXIMITY INTENSITY
        distance_au = position.get("distance_au", 1.0)
        intensity_proximity = 1 / distance_au
        intensity_proximity = min(intensity_proximity, 10)  # Cap so it's not extreme
        # print(f"[LOG] distance_au: {distance_au:.3f}, intensity_proximity (capped): {intensity_proximity:.3f}")

        # 2) VISIBILITY FACTOR (Altitude)
        altitude = position.get("altitude", 0)
        if altitude >= 0:
            visibility_factor = altitude / 90
        else:
            # If below horizon, reduce factor significantly but never below 0.1
            visibility_factor = max((altitude / 90) * 0.4, 0.1)
        # print(f"[LOG] altitude: {altitude:.2f}, visibility_factor: {visibility_factor:.3f}")

        # 3) RULING BONUSES
        bonus = 0
        if planet_name == hour_ruler and planet_name == day_ruling_planet:
            bonus += 1.5  # smaller bonus if it rules both simultaneously
            # print(f"[LOG] {planet_name} rules both hour & day -> bonus = {bonus}")
        elif planet_name == hour_ruler:
            bonus += 9.0
            # print(f"[LOG] {planet_name} is the hour ruler -> bonus = {bonus}")
        elif planet_name == day_ruling_planet:
            bonus += 6.5
            # print(f"[LOG] {planet_name} is the day ruler -> bonus = {bonus}")

        # 4) DIGNITY MODIFIER
        sign = position.get("sign", "")
        dignity_modifier = HeatmapCalculator.calculate_dignity_modifier(planet_name, sign)
        # print(f"[LOG] sign: {sign}, dignity_modifier: {dignity_modifier:.2f}")

        # 5) COMBUSTION & CAZIMI
        combustion_data = HeatmapCalculator.calculate_combustion_cazimi_modifier(position)
        combustion_modifier = combustion_data["combustion_modifier"]
        combustion_status = combustion_data["combustion_status"]
        # print(f"[LOG] combustion_modifier: {combustion_modifier:.2f}, combustion_status: {combustion_status}")

        # 6) MOON-SPECIFIC PHASE MODIFIER
        phase_modifier = 0
        if planet_name == "Moon":
            phase_modifier_data = HeatmapCalculator.calculate_moon_phase_modifier(position)
            phase_modifier = phase_modifier_data["phase_modifier"]
            # print(f"[LOG] Moon phase_modifier: {phase_modifier:.2f}")

        # 7) FINAL INTENSITY CALCULATION
        intensity = (
            0.15 * intensity_proximity +
            0.20 * visibility_factor +
            0.2  * dignity_modifier +
            0.40  * bonus +
            0.10  * phase_modifier +
            combustion_modifier
        )
        intensity = min(max(intensity * 1.5, 0), 10)  # Scale up by 1.5x but cap at 10
        intensity = round(intensity, 2)

        # print(f"[LOG] >>> Final intensity for {planet_name}: {intensity:.2f}")
        # print("[LOG] ----------------------------------------\n")

        # Return numeric intensity + a label if combust/cazimi
        return intensity, combustion_status


    
    
    @staticmethod
    def calculate_gradient_properties(planet_name: str, intensity: float, normalized_size: float, hour_ruler: str, day_ruling_planet: str) -> dict:
        """
        Refined gradient generation with balanced ruling effects and dynamic scaling.
        """
        # print(f"\n[LOG] --- Calculating gradient for {planet_name} ---")
        # print(f"[LOG] Incoming normalized_size: {normalized_size:.2f}")
        # print(f"[LOG] Incoming intensity: {intensity:.2f}")
        
        # Verify planet colors
        planet_colors = PLANETARY_COLORS.get(planet_name)
        if not planet_colors or not isinstance(planet_colors, dict):
            return HeatmapCalculator._default_gradient(planet_name, normalized_size)
        
        gradient_stops = planet_colors.get("gradient_stops")
        if not gradient_stops:
            return HeatmapCalculator._default_gradient(planet_name, normalized_size)
        
        # Ruling multiplier adjustments
        ruling_multiplier = 1.0
        if planet_name == hour_ruler and planet_name == day_ruling_planet:
            ruling_multiplier = 2.5  # Rules both
            # print(f"[LOG] {planet_name} rules both hour & day -> multiplier = {ruling_multiplier}")
        elif planet_name == hour_ruler:
            ruling_multiplier = 1.8  # Hour ruler
            # print(f"[LOG] {planet_name} is hour ruler -> multiplier = {ruling_multiplier}")
        elif planet_name == day_ruling_planet:
            ruling_multiplier = 1.3  # Day ruler
            # print(f"[LOG] {planet_name} is day ruler -> multiplier = {ruling_multiplier}")
        
        relative_intensity = intensity / 10
        # print(f"[LOG] Relative intensity (0-1): {relative_intensity:.3f}")
        # print(f"[LOG] Ruling multiplier: {ruling_multiplier}")
        
        # Logarithmic scaling for base size
        base_size = math.log(normalized_size + 1) * 200 * ruling_multiplier
        core_radius = base_size
        
        # Dynamic gradient length based on intensity
        gradient_length = base_size * (0.2 + relative_intensity * 0.1)
        inner_radius = core_radius + gradient_length * 0.2
        outer_radius = core_radius + gradient_length * 0.4
        
        # print(f"\n[LOG] Size calculations:")
        # print(f"[LOG] Base size (with ruling multiplier) = {base_size:.2f}")
        # print(f"[LOG] Core radius = {core_radius:.2f}")
        # print(f"[LOG] Gradient length = {gradient_length:.2f}")
        # print(f"[LOG] Additional spread beyond core:")
        # print(f"[LOG] - Inner: +{inner_radius - core_radius:.2f}")
        # print(f"[LOG] - Outer: +{outer_radius - core_radius:.2f}")
        
        # Adjust opacity for contrast
        core_opacity = min(1.0, 0.5 + relative_intensity * 0.4 + ruling_multiplier * 0.2)
        inner_opacity = max(0.05, 0.15 * ruling_multiplier)
        outer_opacity = max(0.01, 0.02 * ruling_multiplier)
        
        def opacity_to_hex(opacity):
            opacity = max(0, min(1, opacity))
            return format(int(opacity * 255), '02x').upper()
        
        gradient_data = {
            "core": {
                "radius": core_radius,
                "color": f"{gradient_stops['core']}{opacity_to_hex(core_opacity)}"
            },
            "inner": {
                "radius": inner_radius,
                "color": f"{gradient_stops['inner']}{opacity_to_hex(inner_opacity)}"
            },
            "outer": {
                "radius": outer_radius,
                "color": f"{gradient_stops['outer']}{opacity_to_hex(outer_opacity)}"
            }
        }
        
        # print(f"[LOG] Final gradient data for {planet_name}: {gradient_data}")
        # print("[LOG] ----------------------------------------\n")
        return gradient_data



    @staticmethod
    def _default_gradient(planet_name: str, normalized_size: float) -> dict:
        """
        Provide a fallback gradient if the planet's colors or gradient stops are missing,
        now with a debug log.
        """
        print(f"[LOG] _default_gradient() called for {planet_name}; normalized_size={normalized_size:.2f}")
        fallback = {
            "core": {
                "radius": normalized_size,
                "color": "#FFFFFF"
            },
            "inner": {
                "radius": normalized_size * 1.5,
                "color": "#DDDDDD"
            },
            "outer": {
                "radius": normalized_size * 2.0,
                "color": "#AAAAAA"
            }
        }
        # print(f"[LOG] Fallback gradient for {planet_name}: {fallback}")
        return fallback
    


   
    @staticmethod
    def calculate_heatmap_properties(ephemeris_data, hour_ruler, day_ruling_planet):
        """
        Process planetary positions to generate heatmap data, accessing fields as dictionaries.

        Args:
            ephemeris_data (dict): Ephemeris data containing "planets" key.
            ruling_planet (str): The planet ruling the current hour.
            day_ruling_planet (str): The planet ruling the current day.

        Returns:
            list: A list of dictionaries, each representing a planet's heatmap data.
        """
        heatmap_data = []
        planetary_positions = ephemeris_data.get("planets", {})
        
        for planet_name, position in planetary_positions.items():
            try:
                # Access fields dynamically from position
                altitude = position.get("altitude", 0)
                azimuth = position.get("azimuth", 0)
                distance_au = position.get("distance_au", 1.0)
                angular_distance = position.get("angular_distance", 1.0)  # Fixed typo here
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
                is_ruling_planet = planet_name.lower() == hour_ruler.lower()
                is_day_ruling_planet = planet_name.lower() == day_ruling_planet.lower()

                # Combustion and cazimi data
                combustion_data = HeatmapCalculator.calculate_combustion_cazimi_modifier(position)

                # Moon-specific modifiers and warnings
                phase_modifier = 0
                moon_warning = None
                if planet_name == "Moon":
                    # Phase modifier
                    moon_phase_data = HeatmapCalculator.calculate_moon_phase_modifier(position)
                    phase_modifier = moon_phase_data["phase_modifier"]
                    # Add Moon-specific warnings
                    moon_warning = []
                    if is_combust:
                        moon_warning.append("The Moon is combust. Avoid critical actions.")
                    if is_out_of_bounds:
                        moon_warning.append("The Moon is out of bounds. Exercise caution in decisions.")

                # Calculate intensity
                intensity = HeatmapCalculator.calculate_planet_intensity(
                    planet_name, position, hour_ruler, day_ruling_planet
                )[0]  # Only take intensity, not status
                
                # Calculate planet normalized size 
                normalized_planet_size = HeatmapCalculator.normalize_planet_size(
                    planet_name,
                    planetary_positions
                )
                
                gradient_props = HeatmapCalculator.calculate_gradient_properties(
                    planet_name, 
                    intensity,
                    normalized_planet_size,
                    hour_ruler,
                    day_ruling_planet 
                )
                
                # Create a heatmap entry
                heatmap_entry = {
                    # Raw Planets Data
                    "planet": planet_name,
                    "altitude": round(altitude, 2),
                    "azimuth": round(azimuth, 2),
                    "distance_au": round(distance_au, 3),
                    "angular_distance": angular_distance,
                    "is_retrograde": is_retrograde,
                    "is_stationary": is_stationary,
                    "daily_motion": daily_motion,
                    "longitude": round(longitude, 2),
                    "sign": sign,
                    "is_ruling_planet": is_ruling_planet,
                    "is_day_ruling_planet": is_day_ruling_planet,
                    "is_cazimi": is_cazimi,
                    "is_combust": is_combust,
                    
                    # Heatmap Calculator Data
                    "combustion_modifier": combustion_data["combustion_modifier"],
                    "combustion_status": combustion_data["combustion_status"],
                    "phase_angle": round(phase_angle, 2) if planet_name == "Moon" else None,
                    "is_out_of_bounds": is_out_of_bounds if planet_name == "Moon" else None,
                    "phase_modifier": phase_modifier,
                    "intensity": intensity,
                    "color": PLANETARY_COLORS[planet_name]["gradient_stops"]["core"],
                    "normalized_planet_size": normalized_planet_size,
                    "gradient": gradient_props,
                    
                    "warnings": moon_warning if planet_name == "Moon" else None,
                }

                heatmap_data.append(heatmap_entry)

            except Exception as e:
                print(f"Error processing {planet_name}: {e}")
                      
        return heatmap_data
    



   
    