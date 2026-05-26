"""
Comprehensive Vedic Astrology Database Schema
Full relational model with proper normalization and foreign keys
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """Define and manage the complete astrology database schema"""
    
    # SQL CREATE STATEMENTS
    CREATE_TABLES = {
        'planets': '''
            CREATE TABLE IF NOT EXISTS planets (
                planet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                sanskrit_name TEXT UNIQUE NOT NULL,
                symbol TEXT,
                day_ruled TEXT,
                metal TEXT,
                color TEXT,
                gem_stone TEXT,
                body_part TEXT,
                sense TEXT,
                friendly_planets TEXT,
                enemy_planets TEXT,
                neutral_planets TEXT,
                guna TEXT,
                tattva TEXT,
                varna TEXT,
                caste TEXT,
                gender TEXT,
                direction TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name)
            )
        ''',
        
        'rashis': '''
            CREATE TABLE IF NOT EXISTS rashis (
                rashi_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                sanskrit_name TEXT UNIQUE NOT NULL,
                symbol TEXT,
                lord_planet_id INTEGER NOT NULL,
                element TEXT,
                quality TEXT,
                direction TEXT,
                color TEXT,
                number INTEGER,
                own_house TEXT,
                exaltation_planet_id INTEGER,
                debilitation_planet_id INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(lord_planet_id) REFERENCES planets(planet_id),
                UNIQUE(rashi_id)
            )
        ''',
        
        'nakshatras': '''
            CREATE TABLE IF NOT EXISTS nakshatras (
                nakshatra_id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                sanskrit_name TEXT UNIQUE NOT NULL,
                ruler_planet_id INTEGER NOT NULL,
                start_degree REAL NOT NULL,
                end_degree REAL NOT NULL,
                deity TEXT,
                animal TEXT,
                nature TEXT,
                guna TEXT,
                tattva TEXT,
                body_part TEXT,
                characteristics TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ruler_planet_id) REFERENCES planets(planet_id),
                UNIQUE(nakshatra_id)
            )
        ''',
        
        'houses': '''
            CREATE TABLE IF NOT EXISTS houses (
                house_number INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                sanskrit_name TEXT NOT NULL,
                significations TEXT,
                karaka_planets TEXT,
                natural_ruler_planet_id INTEGER,
                positive_traits TEXT,
                negative_traits TEXT,
                body_part TEXT,
                disease_area TEXT,
                ai_interpretation_framework TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(natural_ruler_planet_id) REFERENCES planets(planet_id),
                UNIQUE(house_number)
            )
        ''',
        
        'planetary_dignity': '''
            CREATE TABLE IF NOT EXISTS planetary_dignity (
                dignity_id INTEGER PRIMARY KEY AUTOINCREMENT,
                planet_id INTEGER NOT NULL,
                rashi_id INTEGER NOT NULL,
                dignity_type TEXT NOT NULL,
                degrees_range TEXT,
                strength_value INTEGER,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
                FOREIGN KEY(rashi_id) REFERENCES rashis(rashi_id),
                UNIQUE(planet_id, rashi_id, dignity_type)
            )
        ''',
        
        'behavioral_states': '''
            CREATE TABLE IF NOT EXISTS behavioral_states (
                state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                condition_key TEXT UNIQUE NOT NULL,
                condition_name TEXT NOT NULL,
                functional_meaning TEXT,
                ai_prompt_directive TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        
        'planet_house_rulership': '''
            CREATE TABLE IF NOT EXISTS planet_house_rulership (
                rulership_id INTEGER PRIMARY KEY AUTOINCREMENT,
                planet_id INTEGER NOT NULL,
                house_number INTEGER NOT NULL,
                ownership_strength TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
                FOREIGN KEY(house_number) REFERENCES houses(house_number),
                UNIQUE(planet_id, house_number)
            )
        ''',
        
        'chart_snapshots': '''
            CREATE TABLE IF NOT EXISTS chart_snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                calculation_method TEXT,
                birth_date TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                birth_latitude REAL NOT NULL,
                birth_longitude REAL NOT NULL,
                birth_location TEXT,
                timezone TEXT,
                jd_ut REAL,
                ascendant_degree REAL,
                ascendant_rashi_id INTEGER,
                sun_rashi_id INTEGER,
                moon_rashi_id INTEGER,
                chart_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ascendant_rashi_id) REFERENCES rashis(rashi_id),
                FOREIGN KEY(sun_rashi_id) REFERENCES rashis(rashi_id),
                FOREIGN KEY(moon_rashi_id) REFERENCES rashis(rashi_id)
            )
        ''',
        
        'snapshot_planets': '''
            CREATE TABLE IF NOT EXISTS snapshot_planets (
                planet_snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                planet_id INTEGER NOT NULL,
                absolute_degree REAL,
                rashi_id INTEGER NOT NULL,
                rashi_degree REAL,
                nakshatra_id INTEGER,
                house_number INTEGER,
                is_retrograde BOOLEAN,
                is_combust BOOLEAN,
                dignity_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(snapshot_id) REFERENCES chart_snapshots(snapshot_id),
                FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
                FOREIGN KEY(rashi_id) REFERENCES rashis(rashi_id),
                FOREIGN KEY(nakshatra_id) REFERENCES nakshatras(nakshatra_id)
            )
        ''',
        
        'ai_knowledge_base': '''
            CREATE TABLE IF NOT EXISTS ai_knowledge_base (
                knowledge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chart_snapshot_id INTEGER,
                insight_type TEXT,
                planet_id INTEGER,
                house_number INTEGER,
                rashi_id INTEGER,
                learning_content TEXT,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(chart_snapshot_id) REFERENCES chart_snapshots(snapshot_id),
                FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
                FOREIGN KEY(rashi_id) REFERENCES rashis(rashi_id)
            )
        '''
    }
    
    @staticmethod
    def create_database(db_path='jyotish_core.db'):
        """Create all tables with proper schema"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("📦 Creating comprehensive database schema...")
            
            # Create tables in dependency order
            table_order = [
                'planets',
                'rashis',
                'nakshatras',
                'houses',
                'planetary_dignity',
                'behavioral_states',
                'planet_house_rulership',
                'chart_snapshots',
                'snapshot_planets',
                'ai_knowledge_base'
            ]
            
            for table_name in table_order:
                cursor.execute(DatabaseSchema.CREATE_TABLES[table_name])
                print(f"  ✓ Created {table_name} table")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database schema created successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Database creation error: {e}")
            return False


if __name__ == '__main__':
    DatabaseSchema.create_database()
