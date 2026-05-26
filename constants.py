"""
Centralized Vedic Astronomy Constants & Data Mappings
Loads all data from relational database instead of hardcoding
Single source of truth through database relationships
"""

from vedic_data_service import get_vedic_data_service

# Initialize the Vedic Data Service
_vds = None


def _init_service():
    """Initialize Vedic Data Service lazily"""
    global _vds
    if _vds is None:
        _vds = get_vedic_data_service()
    return _vds


# ============================================================================
# HTTP Status Codes
# ============================================================================
HTTP_OK = 200
HTTP_STATUS_OK = 200
HTTP_STATUS_CREATED = 201
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_SERVER_ERROR = 500

# ============================================================================
# Configuration Constants
# ============================================================================
OLLAMA_TIMEOUT = 120
CACHE_TIMEOUT = 3600
ZODIAC_DEGREES = 360
PLANET_COUNT = 9
HOUSE_COUNT = 12
NAKSHATRA_COUNT = 27

# ============================================================================
# DATABASE-DRIVEN FUNCTION INTERFACES
# ============================================================================

def get_planets_list():
    """Get list of all 9 planets from database"""
    service = _init_service()
    return service.get_planet_names_list()


def get_planets_map():
    """Get mapping of planet names to IDs from database"""
    service = _init_service()
    return service.get_planets_map()


def get_rashi_names_dict():
    """Get mapping of rashi IDs to names from database"""
    service = _init_service()
    rashis = service.get_all_rashis()
    return {r['rashi_id']: r['name'] for r in rashis}


def get_rashi_sanskrit_names_dict():
    """Get mapping of rashi IDs to Sanskrit names from database"""
    service = _init_service()
    rashis = service.get_all_rashis()
    return {r['rashi_id']: r['sanskrit_name'] for r in rashis}


def get_sign_lords_dict():
    """Get mapping of rashi IDs to ruling planets from database"""
    service = _init_service()
    rashis = service.get_all_rashis()
    return {r['rashi_id']: r['lord_planet_name'] for r in rashis}


def get_house_names_dict():
    """Get mapping of house numbers to names from database"""
    service = _init_service()
    houses = service.get_all_houses()
    return {h['house_number']: h['name'] for h in houses}


def get_all_houses_dict():
    """Get all house data from database"""
    service = _init_service()
    return service.get_all_houses()


def get_house_by_number(house_number):
    """Get house information by number"""
    service = _init_service()
    return service.get_house_by_number(house_number)


def get_planet_by_name(name):
    """Get planet information by name"""
    service = _init_service()
    return service.get_planet_by_name(name)


def get_all_planets_data():
    """Get all planets with complete data"""
    service = _init_service()
    return service.get_all_planets()


def get_all_rashis_data():
    """Get all rashis with complete data"""
    service = _init_service()
    return service.get_all_rashis()


def get_all_nakshatras_data():
    """Get all nakshatras with complete data"""
    service = _init_service()
    return service.get_all_nakshatras()


def get_nakshatra_from_degree(degree):
    """Get nakshatra that contains the given degree"""
    service = _init_service()
    return service.get_nakshatra_from_degree(degree)


def get_rashi_from_degree(degree):
    """Get rashi that contains the given degree"""
    service = _init_service()
    return service.get_rashi_from_degree(degree)


def get_planet_dignity(planet_id, rashi_id):
    """Get dignity relationship between planet and rashi"""
    service = _init_service()
    return service.get_planet_dignity(planet_id, rashi_id)


def get_planet_dignities_list(planet_id):
    """Get all dignity relationships for a planet"""
    service = _init_service()
    return service.get_planet_dignities(planet_id)


def get_behavioral_state_info(condition_key):
    """Get behavioral state information"""
    service = _init_service()
    return service.get_behavioral_state(condition_key)


def get_all_behavioral_states_list():
    """Get all behavioral states"""
    service = _init_service()
    return service.get_all_behavioral_states()


def get_planet_house_rulers(house_number):
    """Get planets that rule a house"""
    service = _init_service()
    return service.get_house_rulers(house_number)


def get_house_rulership(planet_id):
    """Get houses ruled by a planet"""
    service = _init_service()
    return service.get_planet_house_rulerships(planet_id)


# ============================================================================
# LAZY-LOADED PROPERTIES (Backward compatibility)
# ============================================================================

class _ConstantsProxy:
    """Proxy to provide backward-compatible access to database-driven constants"""
    
    @property
    def PLANETS(self):
        """Get list of all planets"""
        return get_planets_list()
    
    @property
    def RASHI_NAMES(self):
        """Get mapping of rashi IDs to names"""
        return get_rashi_names_dict()
    
    @property
    def SIGN_LORDS(self):
        """Get mapping of rashi IDs to ruling planets (Sanskrit names)"""
        service = _init_service()
        rashis = service.get_all_rashis()
        # Return Sanskrit names for backward compatibility
        return {r['rashi_id']: self._get_planet_sanskrit(r['lord_planet_name']) for r in rashis}
    
    @property
    def PLANET_TRANSLATION(self):
        """Map planet names to Sanskrit"""
        planets = get_all_planets_data()
        return {p['name']: p['sanskrit_name'] for p in planets}
    
    @property
    def HOUSE_NAMES(self):
        """Get mapping of house numbers to names"""
        return get_house_names_dict()
    
    def _get_planet_sanskrit(self, planet_name):
        """Get Sanskrit name of a planet"""
        planet = get_planet_by_name(planet_name)
        return planet['sanskrit_name'] if planet else planet_name


# Create proxy instance
_proxy = _ConstantsProxy()

# Export for backward compatibility
PLANETS = get_planets_list()
RASHI_NAMES = get_rashi_names_dict()
SIGN_LORDS = get_sign_lords_dict()
PLANET_TRANSLATION = None  # Will be loaded on-demand
HOUSE_NAMES = get_house_names_dict()


# ============================================================================
# HELPER FUNCTION TO REINITIALIZE CONSTANTS
# ============================================================================

def reload_constants():
    """Reload all constants from database"""
    global _vds, PLANETS, RASHI_NAMES, SIGN_LORDS, HOUSE_NAMES
    _vds = None
    PLANETS = get_planets_list()
    RASHI_NAMES = get_rashi_names_dict()
    SIGN_LORDS = get_sign_lords_dict()
    HOUSE_NAMES = get_house_names_dict()


if __name__ == '__main__':
    print("✅ Constants loaded from database")
    print(f"  Planets: {len(PLANETS)}")
    print(f"  Rashis: {len(RASHI_NAMES)}")
    print(f"  Houses: {len(HOUSE_NAMES)}")
