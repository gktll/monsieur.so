from datetime import datetime, timedelta, timezone as dt_timezone

from skyfield.almanac import find_discrete, sunrise_sunset
import numpy as np

PLANETARY_ORDER = ['Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter', 'Mars']

def determine_planetary_hour(now_local, sunrise_local, sunset_local):
    """
    Determine the planetary hour and ruling planet for the given local time.
    
    Args:
        now_local (datetime): The current local time.
        sunrise_local (datetime): The local sunrise time.
        sunset_local (datetime): The local sunset time.
    
    Returns:
        tuple: The hour index (0-based) and the ruling planet.
    """
    DAY_RULERS = ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Sun']
    
    # Determine if it's day or night
    if sunrise_local <= now_local <= sunset_local:
        # Daytime calculations
        duration = (sunset_local - sunrise_local).total_seconds() / 12
        time_since_sunrise = (now_local - sunrise_local).total_seconds()
        hour_index = int(time_since_sunrise // duration)
        print(f"DEBUG: Daytime calculation -> Duration per hour: {duration} seconds, Hour index: {hour_index}")
    else:
        # Nighttime calculations
        next_sunrise_local = sunrise_local + timedelta(days=1)
        duration = (next_sunrise_local - sunset_local).total_seconds() / 12
        time_since_sunset = (now_local - sunset_local).total_seconds()
        hour_index = int(time_since_sunset // duration)
        print(f"DEBUG: Nighttime calculation -> Duration per hour: {duration} seconds, Hour index: {hour_index}")
    
    # Determine the ruling planet for the day and hour
    day_index = now_local.weekday()  # 0 = Monday, ..., 6 = Sunday
    day_ruling_planet = DAY_RULERS[day_index]
    start_planet_index = PLANETARY_ORDER.index(day_ruling_planet)
    ruling_planet = PLANETARY_ORDER[(start_planet_index + hour_index) % len(PLANETARY_ORDER)]
    
    print(f"DEBUG: Day ruling planet: {day_ruling_planet}, Start planet index: {start_planet_index}, Ruling planet: {ruling_planet}")
    return hour_index, ruling_planet


def get_sun_times(eph, ts, observer, user_timezone):
    """
    Calculate local sunrise and sunset times using Skyfield's almanac.
    
    Args:
        eph: Skyfield ephemeris object.
        ts: Skyfield timescale object.
        observer: Observer's location in wgs84.
        user_timezone: User's timezone.
    
    Returns:
        tuple: Sunrise and sunset times in the local timezone.
    """
    f = sunrise_sunset(eph, observer)
    
    now_utc = datetime.now(dt_timezone.utc)
    now_local = now_utc.astimezone(user_timezone)
    local_date = now_local.date()
    print(f"DEBUG: Calculating sun times for date: {local_date}")
    
    # Define the time range for the day
    t0 = ts.utc(local_date.year, local_date.month, local_date.day)
    t1 = ts.utc(local_date.year, local_date.month, local_date.day, 23, 59, 59)
    
    # Find discrete sunrise and sunset events
    times, events = find_discrete(t0, t1, f)
    sunrise_indices = np.where(events == 0)[0]
    sunset_indices = np.where(events == 1)[0]
    
    if not sunrise_indices.size or not sunset_indices.size:
        raise ValueError("Could not determine sunrise or sunset times.")
    
    # Convert sunrise and sunset to local time
    sunrise_utc = times[sunrise_indices[0]].utc_datetime()
    sunset_utc = times[sunset_indices[-1]].utc_datetime()
    sunrise_local = sunrise_utc.replace(tzinfo=dt_timezone.utc).astimezone(user_timezone)
    sunset_local = sunset_utc.replace(tzinfo=dt_timezone.utc).astimezone(user_timezone)
    print(f"DEBUG: Raw sunrise UTC: {sunrise_utc}, Raw sunset UTC: {sunset_utc}")
    
    # Handle ordering issues (e.g., swapped sunrise and sunset)
    if sunrise_local > sunset_local:
        sunrise_local, sunset_local = sunset_local, sunrise_local
        print("DEBUG: Swapped sunrise and sunset due to ordering issue.")
    
    return sunrise_local, sunset_local
