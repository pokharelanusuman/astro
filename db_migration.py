"""
Database Migration Script
Migrates from old schema to new relational schema
"""

import sqlite3
import os
import shutil
import logging
from datetime import datetime
from database_schema import DatabaseSchema
from data_seeder import DataSeeder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Manage database migration from old to new schema"""
    
    @staticmethod
    def migrate(db_path='jyotish_core.db', backup=True):
        """Execute the database migration"""
        
        print("\n" + "="*80)
        print("🔄 DATABASE MIGRATION - Old Schema → New Relational Schema")
        print("="*80 + "\n")
        
        # Step 1: Backup old database
        if backup:
            DatabaseMigration._backup_database(db_path)
        
        # Step 2: Remove old database
        print("📦 Removing old database...")
        if os.path.exists(db_path):
            os.remove(db_path)
            print("  ✓ Old database removed")
        
        # Step 3: Create new schema
        print("\n📦 Creating new relational schema...")
        DatabaseSchema.create_database(db_path)
        
        # Step 4: Seed with complete data
        print("\n📦 Seeding database with complete Vedic knowledge...")
        DataSeeder.seed_database(db_path)
        
        # Step 5: Verify migration
        print("\n📦 Verifying migration...")
        DatabaseMigration._verify_migration(db_path)
        
        print("\n" + "="*80)
        print("✅ DATABASE MIGRATION COMPLETE!")
        print("="*80 + "\n")
        
        return True
    
    @staticmethod
    def _backup_database(db_path):
        """Create a backup of the existing database"""
        if not os.path.exists(db_path):
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        
        print(f"📦 Backing up old database to {backup_path}...")
        shutil.copy2(db_path, backup_path)
        print(f"  ✓ Backup created: {backup_path}")
    
    @staticmethod
    def _verify_migration(db_path):
        """Verify the new database has all required data"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            checks = {
                'planets': 'SELECT COUNT(*) FROM planets',
                'rashis': 'SELECT COUNT(*) FROM rashis',
                'nakshatras': 'SELECT COUNT(*) FROM nakshatras',
                'houses': 'SELECT COUNT(*) FROM houses',
                'planetary_dignity': 'SELECT COUNT(*) FROM planetary_dignity',
                'behavioral_states': 'SELECT COUNT(*) FROM behavioral_states',
                'planet_house_rulership': 'SELECT COUNT(*) FROM planet_house_rulership'
            }
            
            print("✅ Data Verification:")
            all_good = True
            
            for table_name, query in checks.items():
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    status = "✓" if count > 0 else "✗"
                    print(f"  {status} {table_name}: {count} records")
                    if count == 0:
                        all_good = False
                except Exception as e:
                    print(f"  ✗ {table_name}: Error - {e}")
                    all_good = False
            
            conn.close()
            
            if all_good:
                print("\n  🎉 All tables have data!")
            
            return all_good
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False


if __name__ == '__main__':
    DatabaseMigration.migrate()
