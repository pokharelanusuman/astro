import math
from abc import ABC, abstractmethod
import swisseph as swe

class EphemerisStrategy(ABC):
    @abstractmethod
    def calculate_chart(self, jd_ut: float, lat: float, lon: float) -> dict:
        pass

class SwissEphemerisStrategy(EphemerisStrategy):
    def __init__(self):
        # Configure Sidereal Engine to Lahiri mode (Chitrapaksha)
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

    def calculate_chart(self, jd_ut: float, lat: float, lon: float) -> dict:
        # Generate raw house cusps using the standard Equal House format
        cusps, ascmc = swe.houses(jd_ut, lat, lon, b'E')
        ascendant = ascmc[0]
        
        flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        
        planets = {
            "Sun": swe.calc_ut(jd_ut, swe.SUN, flag)[0][0],
            "Moon": swe.calc_ut(jd_ut, swe.MOON, flag)[0][0],
            "Mars": swe.calc_ut(jd_ut, swe.MARS, flag)[0][0],
            "Mercury": swe.calc_ut(jd_ut, swe.MERCURY, flag)[0][0],
            "Jupiter": swe.calc_ut(jd_ut, swe.JUPITER, flag)[0][0],
            "Venus": swe.calc_ut(jd_ut, swe.VENUS, flag)[0][0],
            "Saturn": swe.calc_ut(jd_ut, swe.SATURN, flag)[0][0],
            "Rahu": swe.calc_ut(jd_ut, swe.MEAN_NODE, flag)[0][0],
        }
        # Ketu is mathematically locked 180 degrees opposite Rahu
        planets["Ketu"] = (planets["Rahu"] + 180.0) % 360.0
        
        return {"ascendant": ascendant, "planets": planets}

class SuryaSiddhantaStrategy(EphemerisStrategy):
    """Plug-and-play slot for custom Surya Siddhanta logic later."""
    def calculate_chart(self, jd_ut: float, lat: float, lon: float) -> dict:
        pass

class ChartEngine:
    def __init__(self, strategy: EphemerisStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: EphemerisStrategy):
        self.strategy = strategy

    def generate(self, jd_ut: float, lat: float, lon: float) -> dict:
        return self.strategy.calculate_chart(jd_ut, lat, lon)