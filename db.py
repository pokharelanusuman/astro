import sqlite3
import math

DB_PATH = "astrology.db"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )""")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chart_snapshots (
            snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            calculation_method TEXT NOT NULL,
            ascendant_degree REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )""")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_planets (
            snapshot_id INTEGER,
            planet_name TEXT NOT NULL,
            absolute_degree REAL NOT NULL,
            assigned_house INTEGER NOT NULL,
            PRIMARY KEY(snapshot_id, planet_name)
        )""")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS house_dictionary (
            house_number INTEGER PRIMARY KEY,
            significance_tags TEXT NOT NULL
        )""")
        
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS house_impact_graph (
            snapshot_id INTEGER,
            target_house INTEGER,
            source_planet TEXT,
            impact_type TEXT,
            polarity TEXT,
            rationale_chain TEXT,
            PRIMARY KEY(snapshot_id, target_house, source_planet, impact_type)
        )""")
        
    house_meanings = {
        1: "Self, physical body, appearance, character, beginnings.",
        2: "Wealth, speech, family assets, values, immediate education.",
        3: "Courage, sibling communication, short travels, manual skills.",
        4: "Mother, home foundations, peace of mind, property, vehicles.",
        5: "Creativity, children, past-life intelligence, speculation, romance.",
        6: "Debts, obstacles, health challenges, competition, daily employment.",
        7: "Spouse, partnership dynamics, public relations, contracts.",
        8: "Longevity, deep hidden mysteries, transformations, shared wealth.",
        9: "Higher philosophy, destiny, guru, father figures, long journeys.",
        10: "Career status, public achievements, leadership, primary actions.",
        11: "Financial gains, global networks, elder siblings, personal desires.",
        12: "Losses, subconscious patterns, isolation, spiritual liberation."
    }
    
    for h_num, tags in house_meanings.items():
        cursor.execute("INSERT OR IGNORE INTO house_dictionary VALUES (?, ?)", (h_num, tags))
        
    conn.commit()
    conn.close()

def save_and_map_chart(user_id: int, method_name: str, calculated_data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    asc_deg = calculated_data["ascendant"]
    lagna_sign_idx = math.floor(asc_deg / 30.0) + 1
    
    cursor.execute(
        "INSERT INTO chart_snapshots (user_id, calculation_method, ascendant_degree) VALUES (?, ?, ?)",
        (user_id, method_name, asc_deg)
    )
    snapshot_id = cursor.lastrowid
    
    planet_placements = {}
    for p_name, p_deg in calculated_data["planets"].items():
        p_sign_idx = math.floor(p_deg / 30.0) + 1
        assigned_house = (p_sign_idx - lagna_sign_idx + 12) % 12
        if assigned_house == 0:
            assigned_house = 12
            
        planet_placements[p_name] = assigned_house
        cursor.execute("INSERT INTO snapshot_planets VALUES (?, ?, ?, ?)", (snapshot_id, p_name, p_deg, assigned_house))
        
    for target_house in range(1, 13):
        for source_planet, p_house in planet_placements.items():
            if p_house == target_house:
                cursor.execute(
                    "INSERT INTO house_impact_graph VALUES (?, ?, ?, 'Occupant', 'Positive', ?)",
                    (snapshot_id, target_house, source_planet, f"{source_planet} physically occupies House {target_house}.")
                )
                
            dist = (target_house - p_house + 12) % 12
            if dist == 7:
                cursor.execute(
                    "INSERT INTO house_impact_graph VALUES (?, ?, ?, 'Aspect', 'Neutral', ?)",
                    (snapshot_id, target_house, source_planet, f"{source_planet} projects a direct aspect across the 7th-house axis.")
                )
                
    conn.commit()
    conn.close()
    return snapshot_id

def fetch_house_tree(snapshot_id: int, house_num: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT significance_tags FROM house_dictionary WHERE house_number = ?", (house_num,))
    tags = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT source_planet, impact_type, polarity, rationale_chain FROM house_impact_graph WHERE snapshot_id = ? AND target_house = ?",
        (snapshot_id, house_num)
    )
    impacts = cursor.fetchall()
    conn.close()
    
    tree_str = f"🌿 HOUSE {house_num} ARCHITECTURE\n"
    tree_str += f"└── [Core Manifestations]: {tags}\n"
    tree_str += "└── [Relational Influence Nodes]:\n"
    
    if not impacts:
        tree_str += "    └── No direct planet occupants or major aspects."
    for imp in impacts:
        tree_str += f"    ├── Planet: {imp[0]}\n"
        tree_str += f"    │   ├── Lineage: {imp[1]}\n"
        tree_str += f"    │   ├── Default Polarity: {imp[2]}\n"
        tree_str += f"    │   └── Rationale: {imp[3]}\n"
        
    return tree_str