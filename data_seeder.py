"""
Comprehensive Vedic Astrology Data Seeding
Populates all master data with proper relationships and foreign keys
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)

class DataSeeder:
    """Seed the database with complete Vedic knowledge"""
    
    @staticmethod
    def seed_database(db_path='jyotish_core.db'):
        """Seed all data into the database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            print("\n🔄 Seeding Vedic Astrology Database...")
            
            # Step 1: Seed Planets (no dependencies)
            DataSeeder._seed_planets(cursor)
            
            # Step 2: Seed Rashis (depends on planets)
            DataSeeder._seed_rashis(cursor)
            
            # Step 3: Seed Nakshatras (depends on planets)
            DataSeeder._seed_nakshatras(cursor)
            
            # Step 4: Seed Houses (depends on planets)
            DataSeeder._seed_houses(cursor)
            
            # Step 5: Seed Planetary Dignity (depends on planets and rashis)
            DataSeeder._seed_planetary_dignity(cursor)
            
            # Step 6: Seed Behavioral States (no dependencies)
            DataSeeder._seed_behavioral_states(cursor)
            
            # Step 7: Seed Planet-House Rulership (depends on planets and houses)
            DataSeeder._seed_planet_house_rulership(cursor)
            
            conn.commit()
            conn.close()
            
            print("\n🏆 Database seeding complete!\n")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"❌ Data seeding error: {e}")
            return False
    
    @staticmethod
    def _seed_planets(cursor):
        """Seed the planets table"""
        print("📦 Seeding Planets...")
        
        planets = [
            # (name, sanskrit_name, symbol, day, metal, color, gem_stone, body_part, sense, friends, enemies, neutrals, guna, tattva, varna, caste, gender, direction, description)
            ('Sun', 'Surya', '☉', 'Sunday', 'Gold', 'Orange/Red', 'Ruby', 'Heart', 'Sight', 'Moon,Mars,Jupiter', 'Venus', 'Mercury,Saturn', 'Rajas', 'Agni', 'Brahmin', 'Royalty', 'Male', 'East', 'Soul, vitality, core identity, authority, father figure'),
            ('Moon', 'Chandra', '☽', 'Monday', 'Silver', 'White', 'Pearl', 'Brain', 'Taste', 'Sun,Mercury', 'Saturn', 'Mars,Jupiter', 'Sattva', 'Jala', 'Brahmin', 'Royalty', 'Female', 'North', 'Mind, emotions, subconscious, mother, nurturing, public reputation'),
            ('Mars', 'Mangala', '♂', 'Tuesday', 'Copper', 'Red', 'Red Coral', 'Blood/Muscles', 'Smell', 'Sun,Moon,Jupiter', 'Mercury,Venus', 'Saturn', 'Rajas', 'Agni', 'Kshatriya', 'Warrior', 'Male', 'South', 'Courage, energy, conflict, sexuality, violence, surgery'),
            ('Mercury', 'Budha', '☿', 'Wednesday', 'Copper', 'Green', 'Emerald', 'Nervous System', 'Touch', 'Sun,Venus', 'Moon', 'Mars,Jupiter,Saturn', 'Rajas', 'Vayu', 'Vaishya', 'Merchant', 'Neutral', 'North', 'Communication, intellect, trade, commerce, writing, logic'),
            ('Jupiter', 'Brihaspati', '♃', 'Thursday', 'Gold', 'Yellow', 'Yellow Sapphire', 'Liver', 'Taste', 'Sun,Moon,Mars', 'Mercury', 'Venus,Saturn', 'Sattva', 'Akasha', 'Brahmin', 'Priest', 'Male', 'North', 'Wisdom, expansion, luck, spirituality, children, teachers'),
            ('Venus', 'Shukra', '♀', 'Friday', 'Copper', 'White', 'Diamond', 'Reproductive', 'Taste', 'Mercury,Saturn', 'Sun,Moon', 'Mars,Jupiter', 'Rajas', 'Jala', 'Vaishya', 'Artisan', 'Female', 'South', 'Love, beauty, relationships, sexuality, arts, luxury'),
            ('Saturn', 'Shani', '♄', 'Saturday', 'Iron', 'Black/Blue', 'Blue Sapphire', 'Legs/Teeth', 'Touch', 'Mercury,Venus', 'Sun,Moon,Mars', 'Jupiter', 'Tamas', 'Vayu', 'Shudra', 'Servant', 'Neutral', 'West', 'Discipline, karma, longevity, delay, obstacles, service'),
            ('Rahu', 'Rahu', '☊', None, 'Mixed', 'Smoky', 'Hessonite', 'Nervous Disorders', 'All', 'Mercury,Venus,Saturn', 'Sun,Moon', 'Mars,Jupiter', 'Tamas', 'Vayu', 'Mleccha', 'Outcast', 'Neutral', 'South-West', 'Obsession, worldly desires, illusions, foreign lands, technology'),
            ('Ketu', 'Ketu', '☋', None, 'Mixed', 'Smoky', 'Cat\'s Eye', 'Intestines', 'All', 'Mars,Jupiter', 'Sun,Moon', 'Mercury,Venus,Saturn', 'Sattva', 'Akasha', 'Mleccha', 'Outcast', 'Neutral', 'North-West', 'Spirituality, liberation, non-attachment, past-life karma, mysticism')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO planets 
            (name, sanskrit_name, symbol, day_ruled, metal, color, gem_stone, body_part, sense, 
             friendly_planets, enemy_planets, neutral_planets, guna, tattva, varna, caste, gender, direction, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', planets)
        
        print(f"  ✓ Seeded {len(planets)} planets")
    
    @staticmethod
    def _seed_rashis(cursor):
        """Seed the rashis (zodiac signs) table"""
        print("📦 Seeding Rashis (Zodiac Signs)...")
        
        # Get planet IDs for foreign keys
        planets_map = DataSeeder._get_planet_id_map(cursor)
        
        rashis = [
            # (rashi_id, name, sanskrit_name, symbol, lord_planet_id, element, quality, direction, color, number, own_house, description)
            (1, 'Aries', 'Mesha', '♈', planets_map['Mars'], 'Fire', 'Cardinal', 'East', 'Red', 1, '1st', 'Initiative, courage, action, beginning'),
            (2, 'Taurus', 'Vrishabha', '♉', planets_map['Venus'], 'Earth', 'Fixed', 'South', 'White', 2, '2nd', 'Stability, wealth, sensuality, stubborn'),
            (3, 'Gemini', 'Mithuna', '♊', planets_map['Mercury'], 'Air', 'Mutable', 'North', 'Green', 3, '3rd', 'Communication, intellect, adaptability'),
            (4, 'Cancer', 'Karka', '♋', planets_map['Moon'], 'Water', 'Cardinal', 'North', 'White', 4, '4th', 'Emotions, nurturing, home, sensitivity'),
            (5, 'Leo', 'Simha', '♌', planets_map['Sun'], 'Fire', 'Fixed', 'East', 'Orange', 5, '5th', 'Pride, creativity, authority, leadership'),
            (6, 'Virgo', 'Kanya', '♍', planets_map['Mercury'], 'Earth', 'Mutable', 'North', 'Green', 6, '6th', 'Analysis, service, discrimination, health'),
            (7, 'Libra', 'Tula', '♎', planets_map['Venus'], 'Air', 'Cardinal', 'West', 'Black/Blue', 7, '7th', 'Balance, relationships, justice, partnership'),
            (8, 'Scorpio', 'Vrischika', '♏', planets_map['Mars'], 'Water', 'Fixed', 'West', 'Red', 8, '8th', 'Transformation, depth, secrets, occult'),
            (9, 'Sagittarius', 'Dhanu', '♐', planets_map['Jupiter'], 'Fire', 'Mutable', 'North', 'Yellow', 9, '9th', 'Philosophy, wisdom, luck, expansion'),
            (10, 'Capricorn', 'Makara', '♑', planets_map['Saturn'], 'Earth', 'Cardinal', 'South', 'Black', 10, '10th', 'Discipline, structure, authority, ambition'),
            (11, 'Aquarius', 'Kumbha', '♒', planets_map['Saturn'], 'Air', 'Fixed', 'West', 'Dark Blue', 11, '11th', 'Innovation, friendship, ideals, networks'),
            (12, 'Pisces', 'Meena', '♓', planets_map['Jupiter'], 'Water', 'Mutable', 'South', 'Green', 12, '12th', 'Spirituality, compassion, mysticism, escape')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO rashis 
            (rashi_id, name, sanskrit_name, symbol, lord_planet_id, element, quality, direction, color, number, own_house, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rashis)
        
        print(f"  ✓ Seeded {len(rashis)} rashis")
    
    @staticmethod
    def _seed_nakshatras(cursor):
        """Seed all 27 nakshatras with proper relationships"""
        print("📦 Seeding 27 Nakshatras...")
        
        planets_map = DataSeeder._get_planet_id_map(cursor)
        
        nakshatras = [
            # (id, name, sanskrit, ruler_planet_id, start_degree, end_degree, deity, animal, nature, guna, tattva, body_part, characteristics)
            (1, 'Ashwini', 'अश्विनी', planets_map['Ketu'], 0.0, 13.3333, 'Ashwini Kumaras', 'Horse', 'Swift', 'Rajas', 'Agni', 'Head', 'Initiating, pioneer, healer, quick action'),
            (2, 'Bharani', 'भरणी', planets_map['Venus'], 13.3333, 26.6667, 'Yama', 'Elephant', 'Productive', 'Rajas', 'Jala', 'Face', 'Transformative, protective, bearing responsibilities'),
            (3, 'Krittika', 'कृत्तिका', planets_map['Sun'], 26.6667, 40.0, 'Agni', 'Sheep', 'Mixed', 'Rajas', 'Agni', 'Neck', 'Sharp, critical, purifying, cutting'),
            (4, 'Rohini', 'रोहिणी', planets_map['Moon'], 40.0, 53.3333, 'Brahma', 'Serpent', 'Productive', 'Sattva', 'Prithvi', 'Upper Arm', 'Growing, attractive, luxurious, sensual'),
            (5, 'Mrigashira', 'मृगशिरा', planets_map['Mars'], 53.3333, 66.6667, 'Soma', 'Deer', 'Mixed', 'Rajas', 'Vayu', 'Lower Arm', 'Searching, inquisitive, curious, restless'),
            (6, 'Ardra', 'आर्द्रा', planets_map['Rahu'], 66.6667, 80.0, 'Rudra', 'Dog', 'Destructive', 'Rajas', 'Akasha', 'Hands', 'Emotional storm, breakthrough, separation'),
            (7, 'Punarvasu', 'पुनर्वसु', planets_map['Jupiter'], 80.0, 93.3333, 'Aditi', 'Cat', 'Productive', 'Sattva', 'Akasha', 'Belly', 'Return, renewal, resilience, nurturing'),
            (8, 'Pushya', 'पुष्य', planets_map['Saturn'], 93.3333, 106.6667, 'Brihaspati', 'Sheep', 'Productive', 'Sattva', 'Prithvi', 'Heart', 'Nourishing, protective, spiritual, dutiful'),
            (9, 'Ashlesha', 'आश्लेषा', planets_map['Mercury'], 106.6667, 120.0, 'Sarpas', 'Snake', 'Destructive', 'Tamas', 'Jala', 'Intestines', 'Focused, intense, secretive, strategic'),
            (10, 'Magha', 'मघा', planets_map['Ketu'], 120.0, 133.3333, 'Pitris', 'Rat', 'Destructive', 'Rajas', 'Agni', 'Penis', 'Ancestral, powerful, authoritative, proud'),
            (11, 'Purva Phalguni', 'पूर्व फाल्गुनी', planets_map['Venus'], 133.3333, 146.6667, 'Bhaga', 'Rat', 'Productive', 'Rajas', 'Agni', 'Stomach', 'Creative, enjoyment, relaxation, performance'),
            (12, 'Uttara Phalguni', 'उत्तर फाल्गुनी', planets_map['Sun'], 146.6667, 160.0, 'Aryaman', 'Bull', 'Productive', 'Rajas', 'Prithvi', 'Intestines', 'Loyal, honorable, structured, patronage'),
            (13, 'Hasta', 'हस्त', planets_map['Moon'], 160.0, 173.3333, 'Savitar', 'Buffalo', 'Productive', 'Sattva', 'Vayu', 'Hands', 'Skillful, dexterous, cunning, trading'),
            (14, 'Chitra', 'चित्रा', planets_map['Mars'], 173.3333, 186.6667, 'Vishvakarma', 'Tiger', 'Productive', 'Rajas', 'Akasha', 'Heart', 'Architectural, creative, beautiful, design'),
            (15, 'Svati', 'स्वाती', planets_map['Rahu'], 186.6667, 200.0, 'Vayu', 'Swallow', 'Mixed', 'Rajas', 'Vayu', 'Lungs', 'Independent, adaptable, trader, dispersive'),
            (16, 'Vishakha', 'विशाखा', planets_map['Jupiter'], 200.0, 213.3333, 'Indragni', 'Tiger', 'Productive', 'Rajas', 'Jala', 'Genitals', 'Determined, competitive, purposeful, warrior'),
            (17, 'Anuradha', 'अनुराधा', planets_map['Saturn'], 213.3333, 226.6667, 'Mitra', 'Deer', 'Productive', 'Sattva', 'Vayu', 'Hips', 'Devoted, loyal, networking, friendship'),
            (18, 'Jyeshtha', 'ज्येष्ठा', planets_map['Mercury'], 226.6667, 240.0, 'Indra', 'Spider', 'Destructive', 'Rajas', 'Akasha', 'Thighs', 'Senior, protective, esoteric, powerful'),
            (19, 'Mula', 'मूल', planets_map['Ketu'], 240.0, 253.3333, 'Nirriti', 'Dog', 'Destructive', 'Tamas', 'Prithvi', 'Feet', 'Root-seeking, investigation, deconstruction'),
            (20, 'Purva Ashadha', 'पूर्व आषाढ़ा', planets_map['Venus'], 253.3333, 266.6667, 'Apas', 'Monkey', 'Productive', 'Rajas', 'Jala', 'Calves', 'Invincible, persuasive, artistic, proud'),
            (21, 'Uttara Ashadha', 'उत्तर आषाढ़ा', planets_map['Sun'], 266.6667, 280.0, 'Visvedevas', 'Elephant', 'Productive', 'Rajas', 'Prithvi', 'Ankles', 'Victorious, noble, universal, righteous'),
            (22, 'Shravana', 'श्रवण', planets_map['Moon'], 280.0, 293.3333, 'Vishnu', 'Monkey', 'Productive', 'Sattva', 'Akasha', 'Ears', 'Listening, devoted, organized, learning'),
            (23, 'Dhanishta', 'धनिष्ठा', planets_map['Mars'], 293.3333, 306.6667, 'Vasus', 'Lion', 'Productive', 'Rajas', 'Vayu', 'Upper Leg', 'Rhythmic, wealthy, musical, swift'),
            (24, 'Shatabhisha', 'शतभिषा', planets_map['Rahu'], 306.6667, 320.0, 'Varuna', 'Horse', 'Productive', 'Sattva', 'Vayu', 'Knees', 'Hundred healers, network, diagnostic'),
            (25, 'Purva Bhadrapada', 'पूर्व भाद्रपदा', planets_map['Jupiter'], 320.0, 333.3333, 'Aja Ekapada', 'Lion', 'Mixed', 'Rajas', 'Jala', 'Left Side', 'Mystical, dual, esoteric, shadow work'),
            (26, 'Uttara Bhadrapada', 'उत्तर भाद्रपदा', planets_map['Saturn'], 333.3333, 346.6667, 'Ahirbudhnya', 'Cow', 'Productive', 'Sattva', 'Jala', 'Right Side', 'Deep, stable, disciplined, protective'),
            (27, 'Revati', 'रेवती', planets_map['Venus'], 346.6667, 360.0, 'Pushan', 'Elephant', 'Productive', 'Sattva', 'Jala', 'Feet', 'Completion, transition, sanctuary, harmony')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO nakshatras 
            (nakshatra_id, name, sanskrit_name, ruler_planet_id, start_degree, end_degree, deity, animal, nature, guna, tattva, body_part, characteristics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', nakshatras)
        
        print(f"  ✓ Seeded {len(nakshatras)} nakshatras")
    
    @staticmethod
    def _seed_houses(cursor):
        """Seed the 12 houses with their meanings"""
        print("📦 Seeding 12 Houses...")
        
        planets_map = DataSeeder._get_planet_id_map(cursor)
        
        houses = [
            # (house_num, name, sanskrit_name, significations, karaka_planets, natural_ruler_id, positive, negative, body_part, disease_area, ai_framework)
            (1, 'Lagna / Tanu Bhava', 'लग्न / तनु भाव', 
             'Self, physical body, appearance, character, beginnings, health', 
             'Sun', planets_map['Sun'],
             'Confidence, leadership, vitality, self-expression', 'Weakness, confusion, poor health',
             'Head, Face', 'Headaches, facial issues',
             'Analyze overall vitality, physical constitution, and core identity of the native'),
            
            (2, 'Dhana Bhava', 'धन भाव',
             'Wealth, family, speech, food, assets, values',
             'Jupiter, Mercury', planets_map['Jupiter'],
             'Prosperity, eloquence, family bonds', 'Poverty, poor speech, family discord',
             'Mouth, Teeth', 'Speech impediments, throat issues',
             'Examine resource accumulation and familial financial foundations'),
            
            (3, 'Sahaja Bhava', 'सहज भाव',
             'Communication, siblings, courage, short travels, initiative',
             'Mars', planets_map['Mars'],
             'Bravery, intellectual ability, writing', 'Weakness, cowardice, poor communication',
             'Shoulders, Arms', 'Shoulder pain, arm weakness',
             'Evaluate personal willpower and communication abilities'),
            
            (4, 'Sukha Bhava', 'सुख भाव',
             'Mother, home, vehicles, land, emotional stability, happiness',
             'Moon, Mercury', planets_map['Moon'],
             'Peace, comfort, property ownership, maternal love', 'Restlessness, loss of property, tension',
             'Chest, Lungs', 'Chest issues, respiratory problems',
             'Examine inner contentment and domestic foundations'),
            
            (5, 'Putra Bhava', 'पुत्र भाव',
             'Children, intelligence, creativity, speculation, past merits',
             'Jupiter', planets_map['Jupiter'],
             'Intellectual brilliance, children, creative talents', 'Infertility, foolishness, failed speculation',
             'Abdomen, Heart', 'Digestive issues, heart problems',
             'Interpret creative mind and legacy building'),
            
            (6, 'Shatru Bhava', 'शत्रु भाव',
             'Enemies, disease, obstacles, debts, litigation, daily work',
             'Mars, Saturn', planets_map['Mars'],
             'Health, overcoming challenges, service', 'Illness, enemies, debts, failure',
             'Abdomen', 'Stomach issues, digestive disorders',
             'Assess health resilience and problem-solving'),
            
            (7, 'Yuvati Bhava', 'युवती भाव',
             'Marriage, spouse, partnerships, contracts, public dealings',
             'Venus', planets_map['Venus'],
             'Love, partnership, contracts, business', 'Divorce, disputes, broken partnerships',
             'Lower back, Genitals', 'Reproductive issues, back pain',
             'Analyze interpersonal balance and partnership potential'),
            
            (8, 'Randhra Bhava', 'रंध्र भाव',
             'Longevity, transformation, secrets, inheritance, research',
             'Saturn', planets_map['Saturn'],
             'Longevity, occult knowledge, transformation', 'Sudden loss, hidden dangers, chronic illness',
             'Reproductive organs, Anus', 'Chronic diseases, hidden ailments',
             'Look for deep psychological patterns and life transformations'),
            
            (9, 'Dharma Bhava', 'धर्म भाव',
             'Philosophy, wisdom, father, luck, long journeys, mentors',
             'Jupiter, Sun', planets_map['Jupiter'],
             'Luck, wisdom, paternal bonds, spirituality', 'Bad luck, ignorance, lack of mentors',
             'Thighs, Hip', 'Hip issues, sciatica',
             'Evaluate higher belief systems and general fortune'),
            
            (10, 'Karma Bhava', 'कर्म भाव',
             'Career, profession, public image, authority, achievements',
             'Mercury, Sun, Mars', planets_map['Mercury'],
             'Success, recognition, leadership role', 'Failure, bad reputation, unemployment',
             'Knees', 'Knee problems, joint issues',
             'Synthesize professional visibility and achievements'),
            
            (11, 'Labha Bhava', 'लाभ भाव',
             'Gains, desires, elder siblings, networks, cash flow',
             'Jupiter', planets_map['Jupiter'],
             'Gains, friendship, desire fulfillment', 'Losses, unfulfilled wishes, isolation',
             'Calves, Left Ear', 'Calf issues, ear problems',
             'Assess financial flows and social networking'),
            
            (12, 'Vyaya Bhava', 'व्यय भाव',
             'Losses, expenditure, isolation, liberation, foreign lands',
             'Saturn, Ketu', planets_map['Saturn'],
             'Spirituality, enlightenment, foreign success', 'Waste, loss, institutionalization, confusion',
             'Feet', 'Foot problems, infections',
             'Examine subconscious patterns and spiritual release')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO houses
            (house_number, name, sanskrit_name, significations, karaka_planets, natural_ruler_planet_id, positive_traits, negative_traits, body_part, disease_area, ai_interpretation_framework)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', houses)
        
        print(f"  ✓ Seeded {len(houses)} houses")
    
    @staticmethod
    def _seed_planetary_dignity(cursor):
        """Seed planetary dignity relationships (exaltation, debilitation, mulatrikona)"""
        print("📦 Seeding Planetary Dignities...")
        
        planets_map = DataSeeder._get_planet_id_map(cursor)
        rashis_map = DataSeeder._get_rashi_id_map(cursor)
        
        dignities = [
            # (planet_id, rashi_id, dignity_type, degree_range, strength, description)
            (planets_map['Sun'], rashis_map['Aries'], 'EXALTED', '0-10', 10, 'Sun exalted in Aries grants noble leadership and vitality'),
            (planets_map['Sun'], rashis_map['Leo'], 'MULATRIKONA', '0-20', 9, 'Sun mulatrikona in Leo - core rulership'),
            (planets_map['Sun'], rashis_map['Libra'], 'DEBILITATED', '0-10', 1, 'Sun debilitated in Libra causes dependency'),
            
            (planets_map['Moon'], rashis_map['Taurus'], 'EXALTED', '0-3', 10, 'Moon exalted in Taurus gives emotional stability'),
            (planets_map['Moon'], rashis_map['Cancer'], 'MULATRIKONA', '4-30', 9, 'Moon mulatrikona in Cancer - core emotional home'),
            (planets_map['Moon'], rashis_map['Scorpio'], 'DEBILITATED', '0-3', 1, 'Moon debilitated in Scorpio creates turbulent emotions'),
            
            (planets_map['Mars'], rashis_map['Capricorn'], 'EXALTED', '28', 10, 'Mars exalted in Capricorn shows structured energy'),
            (planets_map['Mars'], rashis_map['Aries'], 'MULATRIKONA', '0-12', 9, 'Mars mulatrikona in Aries - core rulership'),
            (planets_map['Mars'], rashis_map['Cancer'], 'DEBILITATED', '0-28', 1, 'Mars debilitated in Cancer creates passive-aggression'),
            
            (planets_map['Mercury'], rashis_map['Virgo'], 'EXALTED', '15', 10, 'Mercury exalted in Virgo delivers analytical brilliance'),
            (planets_map['Mercury'], rashis_map['Gemini'], 'MULATRIKONA', '0-15', 9, 'Mercury mulatrikona in Gemini - core rulership'),
            (planets_map['Mercury'], rashis_map['Pisces'], 'DEBILITATED', '0-15', 1, 'Mercury debilitated in Pisces causes confusion'),
            
            (planets_map['Jupiter'], rashis_map['Cancer'], 'EXALTED', '0-5', 10, 'Jupiter exalted in Cancer amplifies wisdom'),
            (planets_map['Jupiter'], rashis_map['Sagittarius'], 'MULATRIKONA', '0-10', 9, 'Jupiter mulatrikona in Sagittarius - core rulership'),
            (planets_map['Jupiter'], rashis_map['Capricorn'], 'DEBILITATED', '0-5', 1, 'Jupiter debilitated in Capricorn causes rigidity'),
            
            (planets_map['Venus'], rashis_map['Pisces'], 'EXALTED', '27', 10, 'Venus exalted in Pisces gives unconditional love'),
            (planets_map['Venus'], rashis_map['Taurus'], 'MULATRIKONA', '0-15', 9, 'Venus mulatrikona in Taurus - core pleasure'),
            (planets_map['Venus'], rashis_map['Virgo'], 'DEBILITATED', '0-27', 1, 'Venus debilitated in Virgo causes criticism'),
            
            (planets_map['Saturn'], rashis_map['Libra'], 'EXALTED', '20', 10, 'Saturn exalted in Libra shows justice and order'),
            (planets_map['Saturn'], rashis_map['Aquarius'], 'MULATRIKONA', '0-20', 9, 'Saturn mulatrikona in Aquarius - core rulership'),
            (planets_map['Saturn'], rashis_map['Aries'], 'DEBILITATED', '0-20', 1, 'Saturn debilitated in Aries creates frustration'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO planetary_dignity
            (planet_id, rashi_id, dignity_type, degrees_range, strength_value, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', dignities)
        
        print(f"  ✓ Seeded {len(dignities)} planetary dignity relationships")
    
    @staticmethod
    def _seed_behavioral_states(cursor):
        """Seed behavioral states like retrograde, combust, etc."""
        print("📦 Seeding Behavioral States...")
        
        states = [
            ('RETROGRADE', 'Retrograde Motion (Vakri)', 
             'The planet moves in reverse. Energy is internalized and karmic.',
             'This planet is retrograde. Analyze its energy as highly introspective, unconventional, and carrying intense karmic lessons. The native processes this internally before external expression.'),
            
            ('COMBUST', 'Combustion (Asta)', 
             'Planet is very close to the Sun. Authority is burned away.',
             'This planet is combust (very close to Sun). Its external expressions are burned away. The native builds intense internal resilience regarding this planet\'s themes.'),
            
            ('EXALTED', 'Exaltation (Ucha)', 
             'Planet is in its highest dignity. Peak functional strength.',
             'This planet is exalted. It operates at peak efficiency with exceptional confidence, noble qualities, and supreme structural clarity.'),
            
            ('DEBILITATED', 'Debilitation (Neecha)', 
             'Planet is in its lowest dignity. Structural friction.',
             'This planet is debilitated. It faces structural friction and low resource availability, requiring external support for optimal expression.'),
            
            ('DIRECT', 'Direct Motion (Anuvakri)', 
             'Planet moves forward. Normal outward expression.',
             'This planet is in direct motion. It expresses its energy outwardly in normal, conventional ways.'),
            
            ('STATIONARY', 'Stationary Station', 
             'Planet changes from retrograde to direct. Turning point.',
             'This planet is at a station point. Its energy intensifies as it prepares to change direction. A critical turning point for this planet\'s themes.')
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO behavioral_states
            (condition_key, condition_name, functional_meaning, ai_prompt_directive)
            VALUES (?, ?, ?, ?)
        ''', states)
        
        print(f"  ✓ Seeded {len(states)} behavioral states")
    
    @staticmethod
    def _seed_planet_house_rulership(cursor):
        """Seed planet-house rulership relationships"""
        print("📦 Seeding Planet-House Rulership...")
        
        planets_map = DataSeeder._get_planet_id_map(cursor)
        
        rulerships = [
            # Each planet rules certain houses based on zodiac ownership
            (planets_map['Sun'], 1, 'Primary', 'Sun naturally rules 1st house through Leo'),
            (planets_map['Sun'], 5, 'Primary', 'Sun rules 5th house through Leo'),
            (planets_map['Sun'], 9, 'Secondary', 'Sun has association with 9th house'),
            
            (planets_map['Moon'], 2, 'Primary', 'Moon rules 2nd house through Cancer'),
            (planets_map['Moon'], 4, 'Primary', 'Moon rules 4th house through Cancer'),
            
            (planets_map['Mars'], 1, 'Primary', 'Mars rules 1st house through Aries'),
            (planets_map['Mars'], 3, 'Primary', 'Mars rules 3rd house through Aries'),
            (planets_map['Mars'], 6, 'Primary', 'Mars rules 6th house through Scorpio'),
            (planets_map['Mars'], 8, 'Primary', 'Mars rules 8th house through Scorpio'),
            
            (planets_map['Mercury'], 3, 'Primary', 'Mercury rules 3rd house through Gemini'),
            (planets_map['Mercury'], 6, 'Primary', 'Mercury rules 6th house through Virgo'),
            (planets_map['Mercury'], 10, 'Secondary', 'Mercury association with 10th house'),
            
            (planets_map['Jupiter'], 2, 'Secondary', 'Jupiter rules 2nd house through Sagittarius'),
            (planets_map['Jupiter'], 5, 'Secondary', 'Jupiter rules 5th house through Sagittarius'),
            (planets_map['Jupiter'], 9, 'Primary', 'Jupiter rules 9th house through Sagittarius'),
            (planets_map['Jupiter'], 11, 'Primary', 'Jupiter rules 11th house through Sagittarius'),
            
            (planets_map['Venus'], 2, 'Primary', 'Venus rules 2nd house through Taurus'),
            (planets_map['Venus'], 7, 'Primary', 'Venus rules 7th house through Libra'),
            (planets_map['Venus'], 12, 'Primary', 'Venus rules 12th house through Libra'),
            
            (planets_map['Saturn'], 6, 'Secondary', 'Saturn rules 6th house through Capricorn'),
            (planets_map['Saturn'], 8, 'Secondary', 'Saturn rules 8th house through Capricorn'),
            (planets_map['Saturn'], 10, 'Primary', 'Saturn rules 10th house through Capricorn'),
            (planets_map['Saturn'], 11, 'Primary', 'Saturn rules 11th house through Aquarius'),
            (planets_map['Saturn'], 12, 'Primary', 'Saturn rules 12th house through Aquarius'),
        ]
        
        cursor.executemany('''
            INSERT OR REPLACE INTO planet_house_rulership
            (planet_id, house_number, ownership_strength, description)
            VALUES (?, ?, ?, ?)
        ''', rulerships)
        
        print(f"  ✓ Seeded {len(rulerships)} planet-house rulerships")
    
    @staticmethod
    def _get_planet_id_map(cursor):
        """Get a mapping of planet names to IDs"""
        cursor.execute('SELECT planet_id, name FROM planets')
        return {row[1]: row[0] for row in cursor.fetchall()}
    
    @staticmethod
    def _get_rashi_id_map(cursor):
        """Get a mapping of rashi names to IDs"""
        cursor.execute('SELECT rashi_id, name FROM rashis')
        return {row[1]: row[0] for row in cursor.fetchall()}


if __name__ == '__main__':
    DataSeeder.seed_database()
