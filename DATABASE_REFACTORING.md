# 🏗️ DATABASE REFACTORING - Complete Documentation

## 📋 Overview

Your Vedic Astrology application has been refactored with a **professional relational database** that replaces all hardcoded constants with properly normalized data structures. This enables:

- ✅ Single source of truth for all Vedic knowledge
- ✅ Proper foreign key relationships between entities
- ✅ Scalable architecture for future enhancements
- ✅ Data integrity and consistency
- ✅ Easy management and updates
- ✅ Complex queries and relationships

---

## 🗂️ Database Schema (10 Tables)

### 1. **planets** Table
Stores all 9 planets (Grahas) with complete information.

```sql
CREATE TABLE planets (
    planet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,                    -- Sun, Moon, Mars, etc.
    sanskrit_name TEXT UNIQUE NOT NULL,           -- Surya, Chandra, Mangala, etc.
    symbol TEXT,                                  -- ☉, ☽, ♂, etc.
    day_ruled TEXT,                               -- Sunday, Monday, etc.
    metal TEXT,                                   -- Gold, Silver, Copper, etc.
    color TEXT,                                   -- Orange, White, Red, etc.
    gem_stone TEXT,                               -- Ruby, Pearl, Red Coral, etc.
    body_part TEXT,                               -- Heart, Brain, Blood, etc.
    sense TEXT,                                   -- Sight, Taste, Touch, etc.
    friendly_planets TEXT,                        -- Comma-separated list
    enemy_planets TEXT,                           -- Comma-separated list
    neutral_planets TEXT,                         -- Comma-separated list
    guna TEXT,                                    -- Sattva, Rajas, Tamas
    tattva TEXT,                                  -- Agni, Jala, Vayu, Akasha, Prithvi
    varna TEXT,                                   -- Brahmin, Kshatriya, Vaishya, Shudra
    caste TEXT,                                   -- Royalty, Warrior, Merchant, Servant, etc.
    gender TEXT,                                  -- Male, Female, Neutral
    direction TEXT,                               -- East, South, West, North, etc.
    description TEXT,                             -- Full description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Sample Data:**
- Sun (Surya) - Ruled by Sunday, Metal: Gold, Gem: Ruby
- Moon (Chandra) - Ruled by Monday, Metal: Silver, Gem: Pearl
- Mars (Mangala) - Ruled by Tuesday, Metal: Copper, Gem: Red Coral
- ... (9 total planets)

---

### 2. **rashis** Table
Stores all 12 zodiac signs with their attributes and ruling planets.

```sql
CREATE TABLE rashis (
    rashi_id INTEGER PRIMARY KEY,                 -- 1-12
    name TEXT UNIQUE NOT NULL,                    -- Aries, Taurus, Gemini, etc.
    sanskrit_name TEXT UNIQUE NOT NULL,           -- Mesha, Vrishabha, etc.
    symbol TEXT,                                  -- ♈, ♉, ♊, etc.
    lord_planet_id INTEGER NOT NULL,              -- Foreign key to planets table
    element TEXT,                                 -- Fire, Earth, Air, Water
    quality TEXT,                                 -- Cardinal, Fixed, Mutable
    direction TEXT,                               -- East, South, West, North
    color TEXT,                                   -- Associated color
    number INTEGER,                               -- 1-12
    own_house TEXT,                               -- House it naturally rules
    exaltation_planet_id INTEGER,                 -- Foreign key - which planet is exalted
    debilitation_planet_id INTEGER,               -- Foreign key - which planet is debilitated
    description TEXT,                             -- Full description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(lord_planet_id) REFERENCES planets(planet_id)
)
```

**Sample Data:**
- Aries (Mesha) - Ruled by Mars, Fire, Cardinal, East
- Taurus (Vrishabha) - Ruled by Venus, Earth, Fixed, South
- ... (12 total rashis)

---

### 3. **nakshatras** Table
Stores all 27 lunar mansions with their rulers and characteristics.

```sql
CREATE TABLE nakshatras (
    nakshatra_id INTEGER PRIMARY KEY,             -- 1-27
    name TEXT UNIQUE NOT NULL,                    -- Ashwini, Bharani, etc.
    sanskrit_name TEXT UNIQUE NOT NULL,           -- अश्विनी, भरणी, etc.
    ruler_planet_id INTEGER NOT NULL,             -- Foreign key to planets
    start_degree REAL NOT NULL,                   -- 0.0, 13.3333, 26.6667, etc.
    end_degree REAL NOT NULL,                     -- 13.3333, 26.6667, 40.0, etc.
    deity TEXT,                                   -- Ashwini Kumaras, Yama, etc.
    animal TEXT,                                  -- Horse, Elephant, Sheep, etc.
    nature TEXT,                                  -- Swift, Productive, Destructive, etc.
    guna TEXT,                                    -- Sattva, Rajas, Tamas
    tattva TEXT,                                  -- Agni, Jala, Vayu, Akasha, Prithvi
    body_part TEXT,                               -- Head, Face, Neck, etc.
    characteristics TEXT,                         -- Key traits and characteristics
    description TEXT,                             -- Full description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ruler_planet_id) REFERENCES planets(planet_id)
)
```

**Sample Data:**
- Ashwini (27° spacing) - Ruler: Ketu, Deity: Ashwini Kumaras
- Bharani - Ruler: Venus, Deity: Yama
- Krittika - Ruler: Sun, Deity: Agni
- ... (27 total nakshatras)

---

### 4. **houses** Table
Stores all 12 astrological houses with their significations.

```sql
CREATE TABLE houses (
    house_number INTEGER PRIMARY KEY,             -- 1-12
    name TEXT NOT NULL,                           -- Lagna Bhava, Dhana Bhava, etc.
    sanskrit_name TEXT NOT NULL,                  -- लग्न, धन, etc.
    significations TEXT,                          -- Key life areas represented
    karaka_planets TEXT,                          -- Significator planets
    natural_ruler_planet_id INTEGER,              -- Foreign key to planets
    positive_traits TEXT,                         -- Beneficial expressions
    negative_traits TEXT,                         -- Challenging expressions
    body_part TEXT,                               -- Associated body parts
    disease_area TEXT,                            -- Health-related areas
    ai_interpretation_framework TEXT,             -- AI analysis directive
    description TEXT,                             -- Full description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(natural_ruler_planet_id) REFERENCES planets(planet_id)
)
```

**Sample Data:**
- House 1 (Lagna) - Self, physical body, appearance
- House 2 (Dhana) - Wealth, family, speech
- House 7 (Yuvati) - Marriage, partnerships
- ... (12 total houses)

---

### 5. **planetary_dignity** Table
Stores exaltation, debilitation, and mulatrikona relationships.

```sql
CREATE TABLE planetary_dignity (
    dignity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet_id INTEGER NOT NULL,                   -- Foreign key to planets
    rashi_id INTEGER NOT NULL,                    -- Foreign key to rashis
    dignity_type TEXT NOT NULL,                   -- EXALTED, DEBILITATED, MULATRIKONA
    degrees_range TEXT,                           -- e.g., "0-10", "15-20"
    strength_value INTEGER,                       -- 1-10 (weakness to strength)
    description TEXT,                             -- Full explanation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
    FOREIGN KEY(rashi_id) REFERENCES rashis(rashi_id),
    UNIQUE(planet_id, rashi_id, dignity_type)
)
```

**Sample Data:**
- Sun EXALTED in Aries (strength: 10)
- Sun DEBILITATED in Libra (strength: 1)
- Mars EXALTED in Capricorn (strength: 10)
- ... (21 total relationships)

---

### 6. **behavioral_states** Table
Stores planetary conditions like retrograde, combust, etc.

```sql
CREATE TABLE behavioral_states (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    condition_key TEXT UNIQUE NOT NULL,           -- RETROGRADE, COMBUST, EXALTED, etc.
    condition_name TEXT NOT NULL,                 -- Retrograde Motion, Combustion, etc.
    functional_meaning TEXT,                      -- How it affects interpretation
    ai_prompt_directive TEXT,                     -- AI analysis instruction
    description TEXT,                             -- Full description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Sample Data:**
- RETROGRADE: Retrograde Motion (Vakri) - Internalized, karmic energy
- COMBUST: Combustion (Asta) - Burned by Sun, authority stripped
- EXALTED: Exaltation (Ucha) - Peak strength, optimal expression
- DIRECT: Direct Motion (Anuvakri) - Normal outward expression

---

### 7. **planet_house_rulership** Table
Stores which houses are naturally ruled by each planet.

```sql
CREATE TABLE planet_house_rulership (
    rulership_id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet_id INTEGER NOT NULL,                   -- Foreign key to planets
    house_number INTEGER NOT NULL,                -- Foreign key to houses
    ownership_strength TEXT,                      -- Primary, Secondary
    description TEXT,                             -- Rulership explanation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
    FOREIGN KEY(house_number) REFERENCES houses(house_number),
    UNIQUE(planet_id, house_number)
)
```

**Sample Data:**
- Sun rules House 1 (Primary) through Leo
- Moon rules House 2 (Primary) through Cancer
- Mars rules Houses 1, 3, 6, 8 through Aries and Scorpio
- Jupiter rules Houses 2, 5, 9, 11
- ... (24 total relationships)

---

### 8. **chart_snapshots** Table
Stores calculated birth charts.

```sql
CREATE TABLE chart_snapshots (
    snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,                                 -- Optional user reference
    calculation_method TEXT,                      -- Method used (Lahiri, etc.)
    birth_date TEXT NOT NULL,                     -- YYYY-MM-DD
    birth_time TEXT NOT NULL,                     -- HH:MM:SS
    birth_latitude REAL NOT NULL,                 -- Geographic latitude
    birth_longitude REAL NOT NULL,                -- Geographic longitude
    birth_location TEXT,                          -- City, Country
    timezone TEXT,                                -- Timezone name
    jd_ut REAL,                                   -- Julian Day UT
    ascendant_degree REAL,                        -- Ascendant zodiacal degree
    ascendant_rashi_id INTEGER,                   -- Foreign key to rashis
    sun_rashi_id INTEGER,                         -- Foreign key to rashis
    moon_rashi_id INTEGER,                        -- Foreign key to rashis
    chart_data TEXT,                              -- JSON of complete chart
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ascendant_rashi_id) REFERENCES rashis(rashi_id),
    FOREIGN KEY(sun_rashi_id) REFERENCES rashis(rashi_id),
    FOREIGN KEY(moon_rashi_id) REFERENCES rashis(rashi_id)
)
```

---

### 9. **snapshot_planets** Table
Stores planetary positions in calculated charts.

```sql
CREATE TABLE snapshot_planets (
    planet_snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL,                 -- Foreign key to chart_snapshots
    planet_id INTEGER NOT NULL,                   -- Foreign key to planets
    absolute_degree REAL,                         -- Zodiacal degree (0-360)
    rashi_id INTEGER NOT NULL,                    -- Foreign key to rashis
    rashi_degree REAL,                            -- Degree within sign (0-30)
    nakshatra_id INTEGER,                         -- Foreign key to nakshatras
    house_number INTEGER,                         -- House placement (1-12)
    is_retrograde BOOLEAN,                        -- Retrograde flag
    is_combust BOOLEAN,                           -- Combust flag
    dignity_type TEXT,                            -- EXALTED, DEBILITATED, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(snapshot_id) REFERENCES chart_snapshots(snapshot_id),
    FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
    FOREIGN KEY(rashi_id) REFERENCES rashis(rashi_id),
    FOREIGN KEY(nakshatra_id) REFERENCES nakshatras(nakshatra_id)
)
```

---

### 10. **ai_knowledge_base** Table
Stores AI-generated insights and learning.

```sql
CREATE TABLE ai_knowledge_base (
    knowledge_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_snapshot_id INTEGER,                    -- Foreign key to chart_snapshots
    insight_type TEXT,                            -- Type of insight
    planet_id INTEGER,                            -- Foreign key to planets
    house_number INTEGER,                         -- House number
    rashi_id INTEGER,                             -- Foreign key to rashis
    learning_content TEXT,                        -- AI-generated content
    confidence_score REAL,                        -- Confidence level (0-1)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chart_snapshot_id) REFERENCES chart_snapshots(snapshot_id),
    FOREIGN KEY(planet_id) REFERENCES planets(planet_id),
    FOREIGN KEY(rashi_id) REFERENCES rashis(rashi_id)
)
```

---

## 📊 Current Database Contents

### Data Loaded:
- **Planets**: 9 records
- **Rashis**: 12 records
- **Nakshatras**: 27 records
- **Houses**: 12 records
- **Planetary Dignity**: 21 relationships
- **Behavioral States**: 6 conditions
- **Planet-House Rulership**: 24 relationships

### Total Relationships: **90+ foreign key relationships**

---

## 🔄 Migration Process

### What Was Done:

1. **Old Schema** (init_db.py, seed_jyotish_data.py):
   - 4 tables with minimal relationships
   - Hardcoded data in Python code
   - Limited query capabilities

2. **New Schema** (database_schema.py, data_seeder.py):
   - 10 properly normalized tables
   - Complete relational design
   - 90+ foreign key relationships
   - All data in database, nothing hardcoded

3. **Migration** (db_migration.py):
   - Backed up old database
   - Created new schema
   - Seeded all Vedic knowledge
   - Verified data integrity

---

## 🛠️ New Tools & Services

### 1. **VedicDataService** (vedic_data_service.py)
Loads all Vedic knowledge from the database. Replaces hardcoded constants.

```python
from vedic_data_service import get_vedic_data_service

vds = get_vedic_data_service()

# Get planets
planets = vds.get_all_planets()
sun = vds.get_planet_by_name('Sun')

# Get rashis
rashis = vds.get_all_rashis()
rashi_from_degree = vds.get_rashi_from_degree(15.5)

# Get nakshatras
nakshatras = vds.get_all_nakshatras()
nak_from_degree = vds.get_nakshatra_from_degree(45.0)

# Get houses
houses = vds.get_all_houses()
house = vds.get_house_by_number(7)

# Get dignities
dignity = vds.get_planet_dignity(planet_id=1, rashi_id=5)
exaltation = vds.get_exaltation_info(planet_id=1)

# Get behavioral states
states = vds.get_all_behavioral_states()
retrograde_state = vds.get_behavioral_state('RETROGRADE')
```

### 2. **Updated Constants** (constants.py)
Now loads all data from database instead of hardcoding.

```python
# All these now query the database:
PLANETS = get_planets_list()
RASHI_NAMES = get_rashi_names_dict()
SIGN_LORDS = get_sign_lords_dict()
HOUSE_NAMES = get_house_names_dict()
```

### 3. **Updated Services**
Services now use VedicDataService for lookups.

```python
# In chart_service.py
vds = get_vedic_data_service()
planet_data = vds.get_planet_by_name('Sun')
rashi_data = vds.get_rashi_from_degree(degree)
```

---

## 💾 Files Created/Modified

### New Files:
- ✅ `database_schema.py` - Schema definition
- ✅ `data_seeder.py` - Data population
- ✅ `vedic_data_service.py` - Data access layer
- ✅ `db_migration.py` - Migration script
- ✅ `DATABASE_REFACTORING.md` - This documentation

### Modified Files:
- ✅ `constants.py` - Now loads from database
- ✅ `services/chart_service.py` - Uses VedicDataService

### Database:
- ✅ `jyotish_core.db` - New relational database
- ✅ `jyotish_core.db.backup_*` - Backup of old database

---

## 🚀 Usage Examples

### Example 1: Get Planet Information
```python
from vedic_data_service import get_vedic_data_service

vds = get_vedic_data_service()
sun = vds.get_planet_by_name('Sun')
print(f"{sun['name']} ({sun['sanskrit_name']})")
print(f"Metal: {sun['metal']}, Gem: {sun['gem_stone']}")
```

### Example 2: Get Rashi from Degree
```python
from vedic_data_service import get_vedic_data_service

vds = get_vedic_data_service()
rashi = vds.get_rashi_from_degree(45.5)
print(f"Degree 45.5 is in {rashi['name']} ({rashi['sanskrit_name']})")
```

### Example 3: Get Nakshatra from Degree
```python
from vedic_data_service import get_vedic_data_service

vds = get_vedic_data_service()
nak = vds.get_nakshatra_from_degree(123.45)
print(f"Nakshatra: {nak['name']}, Ruler: {nak['ruler_planet_name']}")
```

### Example 4: Get House Information
```python
from vedic_data_service import get_vedic_data_service

vds = get_vedic_data_service()
house = vds.get_house_by_number(7)
print(f"{house['name']}: {house['significations']}")
```

### Example 5: Get Exaltation Info
```python
from vedic_data_service import get_vedic_data_service

vds = get_vedic_data_service()
exalt = vds.get_exaltation_info(planet_id=1)  # Sun
print(f"{exalt['planet_name']} is exalted in {exalt['rashi_name']}")
```

---

## 🔍 Query Examples

### Get all planets with their ruling days:
```sql
SELECT name, sanskrit_name, day_ruled, metal, color, gem_stone
FROM planets
ORDER BY planet_id;
```

### Get all rashis and their lords:
```sql
SELECT r.name, p.name as lord_planet, r.element, r.quality
FROM rashis r
JOIN planets p ON r.lord_planet_id = p.planet_id
ORDER BY r.rashi_id;
```

### Get a planet's exaltation and debilitation:
```sql
SELECT pd.dignity_type, r.name, pd.degrees_range, pd.strength_value
FROM planetary_dignity pd
JOIN rashis r ON pd.rashi_id = r.rashi_id
WHERE pd.planet_id = 1 AND pd.dignity_type IN ('EXALTED', 'DEBILITATED');
```

### Get all nakshatras with their rulers:
```sql
SELECT n.name, p.name as ruler, n.deity, n.start_degree, n.end_degree
FROM nakshatras n
JOIN planets p ON n.ruler_planet_id = p.planet_id
ORDER BY n.nakshatra_id;
```

---

## ✅ Benefits

1. **Single Source of Truth**
   - All Vedic knowledge in one place
   - No hardcoded constants to update

2. **Data Integrity**
   - Foreign key relationships ensure consistency
   - Can't have orphaned records

3. **Scalability**
   - Easy to add new data
   - Can extend schema as needed

4. **Performance**
   - Caching via Python layer
   - Optimized queries

5. **Maintainability**
   - Clear separation of data and code
   - Easy to understand relationships

6. **Extensibility**
   - Can add more tables easily
   - Can add more relationships
   - Can track historical data

---

## 🔄 Next Steps

1. ✅ Database refactoring complete
2. Next: Update remaining services to use VedicDataService
3. Next: Add more queries to VedicDataService as needed
4. Next: Create API endpoints for database data
5. Next: Add admin interface for managing data

---

## 📞 Support

For questions about the database:
1. Review this documentation
2. Check `vedic_data_service.py` for available methods
3. Review `database_schema.py` for table definitions
4. Look at `data_seeder.py` for sample data structure

---

**Database Refactoring Complete! 🎉**

Your Vedic Astrology application now has a professional relational database with proper normalization, foreign keys, and clean data relationships.
