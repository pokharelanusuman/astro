import sqlite3

def initialize_astrology_database():
    conn = sqlite3.connect('jyotish_core.db')
    cursor = conn.cursor()
    
    print("⚡ Initializing Vedic Knowledge Matrix Tables...")

    # 1. HOUSE CONFIGURATION MATRIX
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS house_rules (
            house_number INTEGER PRIMARY KEY,
            sanskrit_name TEXT,
            significations TEXT, -- Comma-separated core areas (e.g., Wealth, Career)
            karaka_planets TEXT   -- Significator planets (e.g., Sun for 1st House)
        )
    ''')

    # 2. SIGN DIGNITIES & ELEVATION MATRIX (Exaltation, Debilitation, Moolatrikona)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planetary_dignities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planet TEXT,
            exalted_sign_id INTEGER,
            exaltation_deep_degree REAL,
            debilitated_sign_id INTEGER,
            moolatrikona_sign_id INTEGER,
            moolatrikona_degree_range TEXT
        )
    ''')

    # 3. CONSTELLATION MATRIX (27 Nakshatras & Degree Spans)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nakshatra_rules (
            nakshatra_id INTEGER PRIMARY KEY,
            name TEXT,
            ruler TEXT,
            start_degree REAL, -- Absolute longitude degrees (0 to 360)
            end_degree REAL,
            element_nature TEXT
        )
    ''')

    # 4. BEHAVIORAL STATE RULES (Retrogrades & Combat States)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS behavioral_rules (
            condition_key TEXT PRIMARY KEY,
            functional_effect TEXT,
            ai_prompt_directive TEXT
        )
    ''''')

    # ==========================================================================
    # POPULATE REFERENCE DATA
    # ==========================================================================
    
    # Populate Houses
    houses_data = [
        (1, 'Lagna / Tanu Bhava', 'Self, physical body, appearance, character, beginnings', 'Sun'),
        (2, 'Dhana Bhava', 'Wealth, speech, family, food intake, assets', 'Jupiter, Mercury'),
        (3, 'Sahaja Bhava', 'Courage, younger siblings, communication, short travels, initiative', 'Mars'),
        (4, 'Sukha Bhava', 'Mother, happiness, home, vehicles, land, emotional stability', 'Moon, Mercury'),
        (5, 'Putra Bhava', 'Intelligence, children, creativity, past-life merits (Purva Punya), speculation', 'Jupiter'),
        (6, 'Shatru / Roga Bhava', 'Enemies, disease, debts, daily work, litigation, obstacles', 'Mars, Saturn'),
        (7, 'Yuvati Bhava', 'Marriage, spouse, partnerships, business relations, public dealings', 'Venus'),
        (8, 'Randhra Bhava', 'Longevity, transformations, hidden secrets, unearned wealth, chronic illness', 'Saturn'),
        (9, 'Dharma Bhava', 'Luck, father, higher philosophy, religion, long-distance journeys, mentors', 'Jupiter, Sun'),
        (10, 'Karma Bhava', 'Profession, career status, reputation, public authority, achievements', 'Mercury, Jupiter, Sun, Mars'),
        (11, 'Labha Bhava', 'Gains, desires, elder siblings, cash flow, social networks', 'Jupiter'),
        (12, 'Vyaya Bhava', 'Losses, expenditure, isolation, liberation (Moksha), foreign lands, sleep', 'Saturn, Ketu')
    ]
    cursor.executemany('INSERT OR REPLACE INTO house_rules VALUES (?,?,?,?)', houses_data)

    # Populate Dignities
    dignities_data = [
        ('Sun', 1, 10.0, 7, 5, '0-20'),       # Exalted in Aries (1), Debilitated in Libra (7)
        ('Moon', 2, 3.0, 8, 2, '4-30'),       # Exalted in Taurus (2), Debilitated in Scorpio (8)
        ('Mars', 10, 28.0, 4, 1, '0-12'),     # Exalted in Capricorn (10), Debilitated in Cancer (4)
        ('Mercury', 6, 15.0, 12, 6, '16-20'), # Exalted in Virgo (6), Debilitated in Pisces (12)
        ('Jupiter', 4, 5.0, 10, 9, '0-10'),   # Exalted in Cancer (4), Debilitated in Capricorn (10)
        ('Venus', 12, 27.0, 6, 12, '0-29'),   # Exalted in Pisces (12), Debilitated in Virgo (6)
        ('Saturn', 7, 20.0, 1, 11, '0-20')    # Exalted in Libra (7), Debilitated in Aries (1)
    ]
    cursor.executemany('''
        INSERT OR REPLACE INTO planetary_dignities 
        (planet, exalted_sign_id, exaltation_deep_degree, debilitated_sign_id, moolatrikona_sign_id, moolatrikona_degree_range) 
        VALUES (?,?,?,?,?,?)
    ''', dignities_data)

    # Populate Sample Nakshatras (First 3 for structural validation)
    nakshatra_data = [
        (1, 'Ashwini', 'Ketu', 0.0, 13.3333, 'Gentle, swift, healing energy'),
        (2, 'Bharani', 'Venus', 13.3333, 26.6666, 'Fierce, transformative, restraining energy'),
        (3, 'Krittika', 'Sun', 26.6666, 40.0, 'Mixed, sharp, purifying fire energy')
    ]
    cursor.executemany('INSERT OR REPLACE INTO nakshatra_rules VALUES (?,?,?,?,?,?)', nakshatra_data)

    # Populate Behavioral/State Prompts
    behavioral_data = [
        ('RETROGRADE', 'Internalized, delayed, unconventional expression of energy.', 
         'Analyze this planet as retrograde (Vakri). It is highly potent but acts in an introspective, karmic manner.'),
        ('EXALTED', 'Peak functional operational strength, supreme focus, structural clarity.', 
         'Analyze this planet as Exalted (Ucha). It behaves with exceptional confidence and noble qualities.'),
        ('DEBILITATED', 'Structural friction, low resource availability, defensive expressions.', 
         'Analyze this planet as Debilitated (Neecha). Its natural expressions are challenged, needing external support.')
    ]
    cursor.executemany('INSERT OR REPLACE INTO behavioral_rules VALUES (?,?,?)', behavioral_data)

    conn.commit()
    conn.close()
    print("✅ Database configurations written successfully to 'jyotish_core.db'.")

if __name__ == '__main__':
    initialize_astrology_database()