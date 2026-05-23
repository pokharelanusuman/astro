import sqlite3

def seed_complete_vedic_matrix():
    conn = sqlite3.connect('jyotish_core.db')
    cursor = conn.cursor()
    
    print("🔄 Dropping old tables to refresh clean structural schema...")
    cursor.execute("DROP TABLE IF EXISTS house_rules")
    cursor.execute("DROP TABLE IF EXISTS planetary_dignities")
    cursor.execute("DROP TABLE IF EXISTS nakshatra_rules")
    cursor.execute("DROP TABLE IF EXISTS behavioral_rules")

    # 1. CREATE TABLES WITH EXPLICIT AI DIRECTIVE COLUMNS
    cursor.execute('''
        CREATE TABLE house_rules (
            house_number INTEGER PRIMARY KEY,
            sanskrit_name TEXT,
            significations TEXT,
            karaka_planets TEXT,
            ai_interpretation_framework TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE planetary_dignities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            planet TEXT,
            exalted_sign_id INTEGER,
            exaltation_deep_degree REAL,
            debilitated_sign_id INTEGER,
            moolatrikona_sign_id INTEGER,
            ai_dignity_directive TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE nakshatra_rules (
            nakshatra_id INTEGER PRIMARY KEY,
            name TEXT,
            ruler TEXT,
            start_degree REAL,
            end_degree REAL,
            deity TEXT,
            ai_character_trait TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE behavioral_rules (
            condition_key TEXT PRIMARY KEY,
            functional_meaning TEXT,
            ai_prompt_directive TEXT
        )
    ''')

    print("📦 Seeding Core House Logic...")
    houses = [
        (1, 'Lagna / Tanu Bhava', 'Self, appearance, character, health, beginnings', 'Sun', 
         'Focus on the physical body, core identity, and overall vitality of the native.'),
        (2, 'Dhana Bhava', 'Wealth, family, speech, assets, values, food', 'Jupiter, Mercury', 
         'Analyze resource accumulation, primary speech dynamics, and familial foundations.'),
        (3, 'Sahaja Bhava', 'Courage, communication, short travel, younger siblings, initiative', 'Mars', 
         'Evaluate personal willpower, manual dexterity, mental drive, and localized enterprise.'),
        (4, 'Sukha Bhava', 'Mother, home, land, vehicles, emotional happiness', 'Moon, Mercury', 
         'Examine inner contentment, domestic peace, root foundations, and maternal connections.'),
        (5, 'Putra Bhava', 'Intelligence, children, creativity, speculative gains, purva-punya', 'Jupiter', 
         'Interpret the speculative mind, emotional choices, legacy, and past-life creative merits.'),
        (6, 'Shatru Bhava', 'Obstacles, debts, illness, daily workforce, disputes', 'Mars, Saturn', 
         'Assess daily service capacity, physical vitality against ailments, and dynamic problem-solving.'),
        (7, 'Yuvati Bhava', 'Marriage, partnerships, public relations, dynamic interactions', 'Venus', 
         'Analyze primary interpersonal balances, legal contracts, business partnerships, and spouse profile.'),
        (8, 'Randhra Bhava', 'Longevity, transformation, hidden assets, research, chronic cycles', 'Saturn', 
         'Look for deep hidden psychology, unexpected transformations, research abilities, and sudden shifts.'),
        (9, 'Dharma Bhava', 'Philosophy, higher wisdom, father, luck, long journeys', 'Jupiter, Sun', 
         'Evaluate higher belief structures, guiding frameworks, mentor relations, and general fortune.'),
        (10, 'Karma Bhava', 'Career, public profile, authority, status, dynamic executive duty', 'Mercury, Sun, Mars', 
         'Synthesize professional visibility, public accomplishments, authority interaction, and structural legacy.'),
        (11, 'Labha Bhava', 'Gains, desires, social circles, cash flow, major networks', 'Jupiter', 
         'Assess financial cash flow optimization, realized long-term desires, and networking ecosystems.'),
        (12, 'Vyaya Bhava', 'Losses, expenditure, isolation, spiritual liberation, foreign realms', 'Saturn, Ketu', 
         'Examine subconscious processing systems, institutional isolations, foreign relocations, and spiritual releases.')
    ]
    cursor.executemany('INSERT INTO house_rules VALUES (?,?,?,?,?)', houses)

    print("📦 Seeding Planetary Elevation/Dignity Limits...")
    dignities = [
        ('Sun', 1, 10.0, 7, 5, 'Sun is Exalted in Aries (1) and Debilitated in Libra (7). Exalted Sun grants noble leadership, high ego structural stability. Debilitated Sun causes dependency and struggles with self-identity.'),
        ('Moon', 2, 3.0, 8, 2, 'Moon is Exalted in Taurus (2) and Debilitated in Scorpio (8). Exalted Moon gives unwavering emotional stability and comfort. Debilitated Moon causes turbulent inner processing and anxiety.'),
        ('Mars', 10, 28.0, 4, 1, 'Mars is Exalted in Capricorn (10) and Debilitated in Cancer (4). Exalted Mars channels structured energy into execution. Debilitated Mars creates volatile emotional reactions and passive-aggression.'),
        ('Mercury', 6, 15.0, 12, 6, 'Mercury is Exalted in Virgo (6) and Debilitated in Pisces (12). Exalted Mercury delivers hyper-analytical cognitive talent. Debilitated Mercury results in intuitive but disorganized data management.'),
        ('Jupiter', 4, 5.0, 10, 9, 'Jupiter is Exalted in Cancer (4) and Debilitated in Capricorn (10). Exalted Jupiter amplifies expansive benevolence and wisdom. Debilitated Jupiter can legalistic, rigid, or lack philosophical scope.'),
        ('Venus', 12, 27.0, 6, 12, 'Venus is Exalted in Pisces (12) and Debilitated in Virgo (6). Exalted Venus brings unconditional devotion and artistic refinement. Debilitated Venus causes hyper-criticism in relationships.'),
        ('Saturn', 7, 20.0, 1, 11, 'Saturn is Exalted in Libra (7) and Debilitated in Aries (1). Exalted Saturn handles public justice, diplomacy, and endurance flawlessly. Debilitated Saturn causes internal frustration and lack of discipline.')
    ]
    cursor.executemany('''
        INSERT INTO planetary_dignities 
        (planet, exalted_sign_id, exaltation_deep_degree, debilitated_sign_id, moolatrikona_sign_id, ai_dignity_directive) 
        VALUES (?,?,?,?,?,?)
    ''', dignities)

    print("📦 Seeding Complete 27 Nakshatras Absolute Longitudinal Grid...")
    # Step increment of exactly 13.33333 degrees per Nakshatra zone across 360 degrees
    nakshatras_data = [
        (1, "Ashwini", "Ketu", 0.0, 13.3333, "Ashwini Kumaras", "Swift, pioneer spirit, healing, initiates rapid action."),
        (2, "Bharani", "Venus", 13.3333, 26.6666, "Yama", "Fierce processing, undergoes intense transformations, values justice."),
        (3, "Krittika", "Sun", 26.6666, 40.0, "Agni", "Sharp, razor cutting intellect, purifying force, highly critical."),
        (4, "Rohini", "Moon", 40.0, 53.3333, "Brahma", "Growth, magnetic attraction, fine arts, sensual development, luxury accumulation."),
        (5, "Mrigashira", "Mars", 53.3333, 66.6666, "Soma", "The searcher, inquisitive tracking mind, travel-oriented, analytical research."),
        (6, "Ardra", "Rahu", 66.6666, 80.0, "Rudra", "Emotional storm clearing, breakthrough via chaos, deep psychological cleanup."),
        (7, "Punarvasu", "Jupiter", 80.0, 93.3333, "Aditi", "The return of light, renewal, secondary attempts succeed, deeply nurturing context."),
        (8, "Pushya", "Saturn", 93.3333, 106.6666, "Brihaspati", "Supreme nourishment, structural protection, spiritual law, highly dutiful."),
        (9, "Ashlesha", "Mercury", 106.6666, 120.0, "Sarpas", "Intense focus, strategic insight, hypnotic speech, handling hidden secrets."),
        (10, "Magha", "Ketu", 120.0, 133.3333, "Pitris", "Ancestral pride, royal office, magnetic authority, protective of history and legacy."),
        (11, "Purva Phalguni", "Venus", 133.3333, 146.6666, "Bhaga", "Relaxation, creative leisure, performance arts, processing marital contracts."),
        (12, "Uttara Phalguni", "Sun", 146.6666, 160.0, "Aryaman", "Leadership networks, structural alliances, patron of contracts and relationships."),
        (13, "Hasta", "Moon", 160.0, 173.3333, "Savitar", "Craftsmanship, manual agility, fast calculations, dry humor, trade strategy."),
        (14, "Chitra", "Mars", 173.3333, 186.6666, "Vishvakarma", "Architectural build, structural design brilliance, visual arts, diamond precision."),
        (15, "Svati", "Rahu", 186.6666, 200.0, "Vayu", "Independence, trade navigation, adaptable communication, dispersion of ideas."),
        (16, "Vishakha", "Jupiter", 200.0, 213.3333, "Indragni", "Targeted determination, competitive drive, strategic focus on endgame goals."),
        (17, "Anuradha", "Saturn", 213.3333, 226.6666, "Mitra", "Devotional friendships, long-distance networking coordination, group harmony."),
        (18, "Jyeshtha", "Mercury", 226.6666, 240.0, "Indra", "Seniority shield, protective executive capacity, esoteric insight mastery."),
        (19, "Mula", "Ketu", 240.0, 253.3333, "Nirriti", "Root extraction, deconstruction of reality, investigation of primary causes."),
        (20, "Purva Ashadha", "Venus", 253.3333, 266.6666, "Apas", "Invincible conviction, declaration of capability, artistic fluid movement."),
        (21, "Uttara Ashadha", "Sun", 266.6666, 280.0, "Visvedevas", "Unwavering victory, institutional ethics, structural endurance framework."),
        (22, "Shravana", "Moon", 280.0, 293.3333, "Vishnu", "Active listening, oral traditions memory retention, structural organizational flow."),
        (23, "Dhanishta", "Mars", 293.3333, 306.6666, "Vasus", "Rhythmic wealth structures, musical cadence, group resource optimization."),
        (24, "Shatabhisha", "Rahu", 306.6666, 320.0, "Varuna", "Hundred healers, structural network architecture, handling system diagnostics."),
        (25, "Purva Bhadrapada", "Jupiter", 320.0, 333.3333, "Aja Ekapada", "Dual nature expressions, deep esoteric focus, transformative detachment."),
        (26, "Uttara Bhadrapada", "Saturn", 333.3333, 346.6666, "Ahirbudhnya", "Steady depth foundational stability, deep meditation, balancing complex duties."),
        (27, "Revati", "Venus", 346.6666, 360.0, "Pushan", "Journey completion, transition guidance, sanctuary space, global harmony.")
    ]
    cursor.executemany('INSERT INTO nakshatra_rules VALUES (?,?,?,?,?,?,?)', nakshatras_data)

    print("📦 Seeding Behavioral States Logic...")
    behavioral = [
        ('RETROGRADE', 'Retrograde Motion (Vakri)', 'This planet is moving in reverse relative to Earth. Its energy is highly internalized, unconventional, and carries intense karmic lessons. The native processes this house inwardly before outward expression.'),
        ('COMBUST', 'Combustion (Asta)', 'This planet is within close orbital proximity to the Sun. Its external authority expressions are burned away, forcing the native to build intense internal psychological resilience regarding this planet\'s themes.')
    ]
    cursor.executemany('INSERT INTO behavioral_rules VALUES (?,?,?)', behavioral)

    conn.commit()
    conn.close()
    print("🏆 Initialization Complete! All 27 Nakshatras and AI directives successfully committed to 'jyotish_core.db'.")

if __name__ == '__main__':
    seed_complete_vedic_matrix()