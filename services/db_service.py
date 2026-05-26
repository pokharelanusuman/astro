# Database operations and queries service
import sqlite3
import logging
from config import get_config

logger = logging.getLogger(__name__)
config = get_config()


class DatabaseService:
    """Service for all database operations"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_PATH
    
    def get_connection(self):
        """Get a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Allow dict-like access
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            conn.close()
            return results
        except sqlite3.Error as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def execute_single(self, query, params=None):
        """Execute a query and return single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None
    
    def execute_insert(self, query, params):
        """Execute an INSERT query"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        except sqlite3.Error as e:
            logger.error(f"Insert error: {e}")
            raise
    
    def get_schema(self):
        """Get database schema information"""
        try:
            query = """
                SELECT name, sql FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """
            results = self.execute_query(query)
            return {row[0]: row[1] for row in results}
        except Exception as e:
            logger.error(f"Schema retrieval error: {e}")
            return {}
    
    def get_table_data(self, table_name, limit=100, offset=0):
        """Get data from a specific table with pagination"""
        try:
            # Sanitize table name (basic protection)
            if not table_name.replace('_', '').isalnum():
                raise ValueError(f"Invalid table name: {table_name}")
            
            query = f"SELECT * FROM {table_name} LIMIT ? OFFSET ?"
            results = self.execute_query(query, (limit, offset))
            
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = self.execute_single(count_query)
            total = count_result[0] if count_result else 0
            
            return {
                "data": [dict(row) for row in results],
                "total": total,
                "count": len(results)
            }
        except Exception as e:
            logger.error(f"Table data retrieval error: {e}")
            raise
    
    def fetch_house_tree(self, snapshot_id, house_num):
        """Fetch house-planet data tree for interpretation"""
        try:
            query = """
                SELECT source_planet, impact_type, polarity, rationale_chain
                FROM house_impact_graph
                WHERE snapshot_id = ? AND target_house = ?
            """
            results = self.execute_query(query, (snapshot_id, house_num))
            
            tree = {
                "house": house_num,
                "impacts": [dict(row) for row in results]
            }
            return tree
        except Exception as e:
            logger.error(f"House tree retrieval error: {e}")
            return None
    
    def save_snapshot(self, user_id, method, ascendant_degree, chart_data):
        """Save a chart snapshot to database"""
        try:
            # Insert into chart_snapshots
            snapshot_query = """
                INSERT INTO chart_snapshots 
                (user_id, calculation_method, ascendant_degree)
                VALUES (?, ?, ?)
            """
            snapshot_id = self.execute_insert(
                snapshot_query,
                (user_id, method, ascendant_degree)
            )
            
            # Insert planetary data
            planets_query = """
                INSERT INTO snapshot_planets 
                (snapshot_id, planet_name, absolute_degree, assigned_house)
                VALUES (?, ?, ?, ?)
            """
            
            for planet_name, house_num in chart_data.get("house_mapping", {}).items():
                degree = chart_data["planets"][planet_name]["absolute_degree"]
                self.execute_insert(
                    planets_query,
                    (snapshot_id, planet_name, degree, house_num)
                )
            
            return snapshot_id
        except Exception as e:
            logger.error(f"Snapshot save error: {e}")
            raise
