from app.routes.constants import PLANETARY_COLORS, ESSENTIAL_DIGNITIES


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
    def calculate_planet_intensity(
        planet_name,
        position,
        hour_ruler,
        day_ruling_planet
    ):
        """
        Calculate the intensity of a planet based on various factors.

        Args:
            planet_name (str): Name of the planet being evaluated.
            position (dict): Data for the planet, including altitude, sign, distance, etc.
            ruling_planet (str): Planet ruling the current hour.
            day_ruling_planet (str): Planet ruling the current day.

        Returns:
            tuple: (intensity, combustion_status)
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
        if planet_name == hour_ruler and planet_name == day_ruling_planet:
            bonus += 1.5  # Max bonus for ruling both hour and day
        elif planet_name == hour_ruler:
            bonus += 1.0  # Hour ruler bonus
        elif planet_name == day_ruling_planet:
            bonus += 0.5  # Day ruler bonus

        # Dignity Modifier
        sign = position.get("sign", "")
        dignity_modifier = HeatmapCalculator.calculate_dignity_modifier(planet_name, sign)

        # Combustion and Cazimi Effects
        combustion_data = HeatmapCalculator.calculate_combustion_cazimi_modifier(position)
        combustion_modifier = combustion_data["combustion_modifier"]
        combustion_status = combustion_data["combustion_status"]

        # Moon-Specific Phase Modifier
        phase_modifier = 0
        if planet_name == "Moon":
            phase_modifier_data = HeatmapCalculator.calculate_moon_phase_modifier(position)
            phase_modifier = phase_modifier_data["phase_modifier"]

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

        # Access the planetary positions from the "planets" key
        planetary_positions = ephemeris_data.get("planets", {})

        for planet_name, position in planetary_positions.items():
            try:
                # Access fields dynamically from position
                altitude = position.get("altitude", 0)
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
                    "warnings": moon_warning if planet_name == "Moon" else None,
                }

                heatmap_data.append(heatmap_entry)

            except Exception as e:
                print(f"Error processing {planet_name}: {e}")

        return heatmap_data
