"""
Advanced Database Service - Load all Vedic data from relational database
Replaces hardcoded constants with database queries
"""

import sqlite3
import logging
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class VedicDataService:
    """Service to load and cache all Vedic knowledge from database"""
    
    def __init__(self, db_path='jyotish_core.db'):
        """Initialize the service with database path"""
        self.db_path = db_path
        self._connection = None
        self._cache = {}
    
    def get_connection(self):
        """Get SQLite connection"""
        try:
            if self._connection is None:
                self._connection = sqlite3.connect(self.db_path)
                self._connection.row_factory = sqlite3.Row
            return self._connection
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    # =========================================================================
    # PLANETS - All 9 planets with complete information
    # =========================================================================
    
    def get_all_planets(self) -> List[Dict]:
        """Get all planets with complete data"""
        query = '''
            SELECT * FROM planets 
            ORDER BY planet_id
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_planet_by_name(self, name: str) -> Optional[Dict]:
        """Get planet by name (English or Sanskrit)"""
        query = '''
            SELECT * FROM planets 
            WHERE name = ? OR sanskrit_name = ?
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (name, name))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_planet_by_id(self, planet_id: int) -> Optional[Dict]:
        """Get planet by ID"""
        query = 'SELECT * FROM planets WHERE planet_id = ?'
        cursor = self.get_connection().cursor()
        cursor.execute(query, (planet_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_planets_map(self) -> Dict[str, int]:
        """Get mapping of planet names to IDs"""
        query = 'SELECT planet_id, name FROM planets'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return {row[1]: row[0] for row in cursor.fetchall()}
    
    def get_planet_names_list(self) -> List[str]:
        """Get list of all planet names"""
        query = 'SELECT name FROM planets ORDER BY planet_id'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    
    # =========================================================================
    # RASHIS - All 12 zodiac signs with complete information
    # =========================================================================
    
    def get_all_rashis(self) -> List[Dict]:
        """Get all rashis with complete data"""
        query = '''
            SELECT r.*, p.name as lord_planet_name, p.sanskrit_name as lord_planet_sanskrit
            FROM rashis r
            LEFT JOIN planets p ON r.lord_planet_id = p.planet_id
            ORDER BY r.rashi_id
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_rashi_by_id(self, rashi_id: int) -> Optional[Dict]:
        """Get rashi by ID (1-12)"""
        query = '''
            SELECT r.*, p.name as lord_planet_name
            FROM rashis r
            LEFT JOIN planets p ON r.lord_planet_id = p.planet_id
            WHERE r.rashi_id = ?
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (rashi_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_rashi_by_name(self, name: str) -> Optional[Dict]:
        """Get rashi by English name"""
        query = '''
            SELECT r.*, p.name as lord_planet_name
            FROM rashis r
            LEFT JOIN planets p ON r.lord_planet_id = p.planet_id
            WHERE r.name = ? OR r.sanskrit_name = ?
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (name, name))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_rashi_from_degree(self, degree: float) -> Optional[Dict]:
        """Get rashi that contains the given degree (0-360)"""
        # Normalize degree to 0-360
        degree = degree % 360
        rashi_id = int(degree / 30) + 1
        if rashi_id > 12:
            rashi_id = 12
        return self.get_rashi_by_id(rashi_id)
    
    def get_rashis_map(self) -> Dict[str, int]:
        """Get mapping of rashi names to IDs"""
        query = 'SELECT rashi_id, name FROM rashis'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return {row[1]: row[0] for row in cursor.fetchall()}
    
    def get_rashi_names_list(self) -> List[str]:
        """Get list of all rashi names"""
        query = 'SELECT name FROM rashis ORDER BY rashi_id'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    
    # =========================================================================
    # NAKSHATRAS - All 27 lunar mansions with complete information
    # =========================================================================
    
    def get_all_nakshatras(self) -> List[Dict]:
        """Get all nakshatras with complete data"""
        query = '''
            SELECT n.*, p.name as ruler_planet_name
            FROM nakshatras n
            LEFT JOIN planets p ON n.ruler_planet_id = p.planet_id
            ORDER BY n.nakshatra_id
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_nakshatra_by_id(self, nakshatra_id: int) -> Optional[Dict]:
        """Get nakshatra by ID (1-27)"""
        query = '''
            SELECT n.*, p.name as ruler_planet_name
            FROM nakshatras n
            LEFT JOIN planets p ON n.ruler_planet_id = p.planet_id
            WHERE n.nakshatra_id = ?
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (nakshatra_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_nakshatra_from_degree(self, degree: float) -> Optional[Dict]:
        """Get nakshatra that contains the given degree (0-360)"""
        query = '''
            SELECT n.*, p.name as ruler_planet_name
            FROM nakshatras n
            LEFT JOIN planets p ON n.ruler_planet_id = p.planet_id
            WHERE ? >= n.start_degree AND ? < n.end_degree
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (degree, degree))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_nakshatras_map(self) -> Dict[str, int]:
        """Get mapping of nakshatra names to IDs"""
        query = 'SELECT nakshatra_id, name FROM nakshatras'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return {row[1]: row[0] for row in cursor.fetchall()}
    
    # =========================================================================
    # HOUSES - All 12 houses with complete information
    # =========================================================================
    
    def get_all_houses(self) -> List[Dict]:
        """Get all houses with complete data"""
        query = '''
            SELECT h.*, p.name as ruler_planet_name
            FROM houses h
            LEFT JOIN planets p ON h.natural_ruler_planet_id = p.planet_id
            ORDER BY h.house_number
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_house_by_number(self, house_number: int) -> Optional[Dict]:
        """Get house by number (1-12)"""
        query = '''
            SELECT h.*, p.name as ruler_planet_name
            FROM houses h
            LEFT JOIN planets p ON h.natural_ruler_planet_id = p.planet_id
            WHERE h.house_number = ?
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (house_number,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_houses_map(self) -> Dict[int, str]:
        """Get mapping of house numbers to names"""
        query = 'SELECT house_number, name FROM houses'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    # =========================================================================
    # PLANETARY DIGNITY - Exaltation, Debilitation, Mulatrikona
    # =========================================================================
    
    def get_planet_dignity(self, planet_id: int, rashi_id: int) -> Optional[Dict]:
        """Get dignity relationship between planet and rashi"""
        query = '''
            SELECT * FROM planetary_dignity
            WHERE planet_id = ? AND rashi_id = ?
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (planet_id, rashi_id))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_planet_dignities(self, planet_id: int) -> List[Dict]:
        """Get all dignity relationships for a planet"""
        query = '''
            SELECT pd.*, p.name as planet_name, r.name as rashi_name
            FROM planetary_dignity pd
            JOIN planets p ON pd.planet_id = p.planet_id
            JOIN rashis r ON pd.rashi_id = r.rashi_id
            WHERE pd.planet_id = ?
            ORDER BY pd.dignity_type
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (planet_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_exaltation_info(self, planet_id: int) -> Optional[Dict]:
        """Get exaltation information for a planet"""
        query = '''
            SELECT pd.*, r.name as rashi_name, r.sanskrit_name
            FROM planetary_dignity pd
            JOIN rashis r ON pd.rashi_id = r.rashi_id
            WHERE pd.planet_id = ? AND pd.dignity_type = 'EXALTED'
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (planet_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_debilitation_info(self, planet_id: int) -> Optional[Dict]:
        """Get debilitation information for a planet"""
        query = '''
            SELECT pd.*, r.name as rashi_name, r.sanskrit_name
            FROM planetary_dignity pd
            JOIN rashis r ON pd.rashi_id = r.rashi_id
            WHERE pd.planet_id = ? AND pd.dignity_type = 'DEBILITATED'
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (planet_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_planetary_dignities(self) -> List[Dict]:
        """Get all planetary dignity relationships"""
        query = '''
            SELECT pd.*, p.name as planet_name, r.name as rashi_name
            FROM planetary_dignity pd
            JOIN planets p ON pd.planet_id = p.planet_id
            JOIN rashis r ON pd.rashi_id = r.rashi_id
            ORDER BY pd.dignity_type, pd.planet_id
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # BEHAVIORAL STATES - Retrograde, Combust, etc.
    # =========================================================================
    
    def get_all_behavioral_states(self) -> List[Dict]:
        """Get all behavioral states"""
        query = 'SELECT * FROM behavioral_states ORDER BY state_id'
        cursor = self.get_connection().cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_behavioral_state(self, condition_key: str) -> Optional[Dict]:
        """Get behavioral state by key"""
        query = 'SELECT * FROM behavioral_states WHERE condition_key = ?'
        cursor = self.get_connection().cursor()
        cursor.execute(query, (condition_key,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # =========================================================================
    # PLANET-HOUSE RULERSHIP
    # =========================================================================
    
    def get_planet_house_rulerships(self, planet_id: int) -> List[Dict]:
        """Get houses ruled by a planet"""
        query = '''
            SELECT phr.*, p.name as planet_name, h.name as house_name
            FROM planet_house_rulership phr
            JOIN planets p ON phr.planet_id = p.planet_id
            JOIN houses h ON phr.house_number = h.house_number
            WHERE phr.planet_id = ?
            ORDER BY phr.house_number
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (planet_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_house_rulers(self, house_number: int) -> List[Dict]:
        """Get all planets that rule a house"""
        query = '''
            SELECT phr.*, p.name as planet_name, p.sanskrit_name
            FROM planet_house_rulership phr
            JOIN planets p ON phr.planet_id = p.planet_id
            WHERE phr.house_number = ?
            ORDER BY phr.ownership_strength DESC
        '''
        cursor = self.get_connection().cursor()
        cursor.execute(query, (house_number,))
        return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        cursor = self.get_connection().cursor()
        
        stats = {}
        tables = {
            'planets': 'SELECT COUNT(*) FROM planets',
            'rashis': 'SELECT COUNT(*) FROM rashis',
            'nakshatras': 'SELECT COUNT(*) FROM nakshatras',
            'houses': 'SELECT COUNT(*) FROM houses',
            'planetary_dignity': 'SELECT COUNT(*) FROM planetary_dignity',
            'behavioral_states': 'SELECT COUNT(*) FROM behavioral_states',
            'planet_house_rulership': 'SELECT COUNT(*) FROM planet_house_rulership',
            'chart_snapshots': 'SELECT COUNT(*) FROM chart_snapshots',
        }
        
        for table, query in tables.items():
            cursor.execute(query)
            stats[table] = cursor.fetchone()[0]
        
        return stats
    
    def validate_integrity(self) -> bool:
        """Validate database integrity"""
        try:
            cursor = self.get_connection().cursor()
            
            checks = [
                ('planets', 'SELECT COUNT(*) FROM planets', 9),
                ('rashis', 'SELECT COUNT(*) FROM rashis', 12),
                ('nakshatras', 'SELECT COUNT(*) FROM nakshatras', 27),
                ('houses', 'SELECT COUNT(*) FROM houses', 12),
                ('behavioral_states', 'SELECT COUNT(*) FROM behavioral_states', 6),
            ]
            
            all_valid = True
            for name, query, expected in checks:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                is_valid = count >= expected
                print(f"  {'✓' if is_valid else '✗'} {name}: {count} (expected {expected})")
                all_valid = all_valid and is_valid
            
            return all_valid
        except Exception as e:
            logger.error(f"Integrity check failed: {e}")
            return False


# Global instance
_vds_instance = None


def get_vedic_data_service(db_path='jyotish_core.db') -> VedicDataService:
    """Get or create global VedicDataService instance"""
    global _vds_instance
    if _vds_instance is None:
        _vds_instance = VedicDataService(db_path)
    return _vds_instance


if __name__ == '__main__':
    print("\n🔍 Testing Vedic Data Service...\n")
    
    service = get_vedic_data_service()
    
    # Show stats
    print("📊 Database Statistics:")
    stats = service.get_database_stats()
    for table, count in stats.items():
        print(f"  {table}: {count}")
    
    # Show sample data
    print("\n🪐 Sample Planets:")
    planets = service.get_all_planets()[:3]
    for planet in planets:
        print(f"  - {planet['name']} ({planet['sanskrit_name']})")
    
    print("\n♈ Sample Rashis:")
    rashis = service.get_all_rashis()[:3]
    for rashi in rashis:
        print(f"  - {rashi['name']} ({rashi['sanskrit_name']}) - Ruled by {rashi['lord_planet_name']}")
    
    print("\n🌙 Sample Nakshatras:")
    nakshatras = service.get_all_nakshatras()[:3]
    for nak in nakshatras:
        print(f"  - {nak['name']} ({nak['deity']}) - Ruled by {nak['ruler_planet_name']}")
    
    print("\n✅ Vedic Data Service is ready!\n")
