# Business logic for astrological chart calculations
import swisseph as swe
from datetime import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from config import get_config
import constants as const_module
from vedic_data_service import get_vedic_data_service

config = get_config()
tf = TimezoneFinder()
geolocator = Nominatim(user_agent=config.NOMINATIM_USER_AGENT)

# Initialize Vedic Data Service for database queries
vds = get_vedic_data_service()


class ChartCalculationService:
    """Service for computing Vedic astrology charts"""
    
    def __init__(self):
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        self.calc_flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    
    def calculate_chart(self, year, month, day, hour_str, lat, lon):
        """
        Calculate a complete Vedic astrology chart using Swiss Ephemeris.
        
        Args:
            year, month, day: Birth date
            hour_str: Birth time as "HH:MM" string or decimal
            lat, lon: Birth coordinates
            
        Returns:
            dict: Chart data with planets, houses, and house mapping
        """
        # Parse birth time
        h_part, m_part = self._parse_time(hour_str)
        
        # Get timezone and convert to UTC
        tz_name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        local_dt = datetime(year, month, day, h_part, m_part, 0, tzinfo=ZoneInfo(tz_name))
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        
        # Convert to Julian Day
        jd_ut = swe.julday(
            utc_dt.year, utc_dt.month, utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0
        )
        
        # Calculate house cusps and ascendant
        cusps, ascmc = swe.houses(jd_ut, lat, lon, b'E')
        ascendant_degree = ascmc[0]
        
        # Calculate planetary positions
        planets_data = {}
        planets_list = vds.get_planet_names_list()  # Load from database
        for planet_name in planets_list:
            planet_data = self._get_planet_position(jd_ut, planet_name)
            planets_data[planet_name] = planet_data
        
        # Assign planets to houses
        house_mapping = self._assign_planets_to_houses(planets_data, ascendant_degree)
        
        return {
            "ascendant_degree": ascendant_degree,
            "ascendant_rashi": self._get_rashi_from_degree(ascendant_degree),
            "planets": planets_data,
            "house_mapping": house_mapping,
            "timezone": tz_name,
            "jd_ut": jd_ut,
            "cusps": [float(c) for c in cusps[:12]]
        }
    
    def _parse_time(self, hour_str):
        """Parse time string or decimal to hour and minute"""
        try:
            if ":" in str(hour_str):
                h_part, m_part = map(int, str(hour_str).split(":"))
            else:
                hour_decimal = float(hour_str)
                h_part = int(hour_decimal)
                m_part = int(round((hour_decimal - h_part) * 60))
            return h_part, m_part
        except Exception:
            return 4, 0  # Default to 4:00 AM
    
    def _get_planet_position(self, jd_ut, planet_name):
        """Calculate a planet's position in the zodiac"""
        planet_num = self._planet_name_to_number(planet_name)
        longitude = swe.calc_ut(jd_ut, planet_num, self.calc_flag)[0][0]
        
        # Get planet data from database
        planet_data_db = vds.get_planet_by_name(planet_name)
        sanskrit_name = planet_data_db['sanskrit_name'] if planet_data_db else planet_name
        
        return {
            "name": planet_name,
            "sanskrit_name": sanskrit_name,
            "absolute_degree": float(longitude),
            "rashi": self._get_rashi_from_degree(longitude),
            "rashi_degree": float(longitude % 30)
        }
    
    def _planet_name_to_number(self, planet_name):
        """Convert planet name to Swiss Ephemeris number"""
        planet_map = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mercury": swe.MERCURY,
            "Venus": swe.VENUS,
            "Mars": swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE,
            "Ketu": swe.MEAN_NODE + 1
        }
        return planet_map.get(planet_name, swe.SUN)
    
    def _get_rashi_from_degree(self, degree):
        """Get rashi (sign) from absolute degree using database"""
        rashi_data = vds.get_rashi_from_degree(degree)
        return rashi_data['name'] if rashi_data else "Unknown"
    
    def _assign_planets_to_houses(self, planets_data, ascendant_degree):
        """Assign planets to houses based on their degree"""
        house_mapping = {i: [] for i in range(1, 13)}
        
        for planet_name, planet_data in planets_data.items():
            degree = planet_data["absolute_degree"]
            house = self._get_house_from_degree(degree, ascendant_degree)
            house_mapping[house].append(planet_name)
        
        return house_mapping
    
    def _get_house_from_degree(self, planet_degree, ascendant_degree):
        """Determine which house a planet is in"""
        # Normalize degrees
        planet_norm = planet_degree % 360
        asc_norm = ascendant_degree % 360
        
        # Calculate distance from ascendant
        distance = (planet_norm - asc_norm) % 360
        
        # Determine house (30 degrees per house)
        house = int((distance // 30)) + 1
        return max(1, min(12, house))
    
    def get_location_string(self, lat, lon):
        """Get human-readable location from coordinates"""
        try:
            location = geolocator.reverse(f"{lat}, {lon}")
            address_dict = location.raw.get('address', {})
            
            display_place = (address_dict.get('city') or 
                           address_dict.get('town') or 
                           address_dict.get('county') or 
                           'Unknown')
            country = address_dict.get('country', 'Unknown')
            
            return f"{display_place}, {country}"
        except Exception:
            return f"{lat:.4f}°, {lon:.4f}°"
