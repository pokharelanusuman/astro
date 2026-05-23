import os
import sys
import signal
import psutil
import warnings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, render_template, jsonify, request

import swisseph as swe
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

# Import streamlined direct AI connector engine
from ai_engine import run_direct_astrology_analysis

app = Flask(__name__)
tf = TimezoneFinder()
geolocator = Nominatim(user_agent="jyotish_engine_core_v2")

# ==============================================================================
# ULTIMATE PROCESS REAPER (Optimized for Local Network Binding)
# ==============================================================================
def graceful_shutdown_handler(signum, frame):
    """Suppresses multiprocessing warning messages and drops port bindings cleanly."""
    warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")
    try:
        current_pid = os.getpid()
        parent = psutil.Process(current_pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                if "resource_tracker" in child.name():
                    continue
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        psutil.wait_procs(children, timeout=0.1)
    except Exception:
        pass

    try:
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            os.kill(os.getpid(), signal.SIGKILL)
        else:
            os.killpg(os.getpgrp(), signal.SIGTERM)
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown_handler)
signal.signal(signal.SIGTERM, graceful_shutdown_handler)
# ==============================================================================

# Traditional Vedic Sanskrit Mapping Structures
RASHI_NAMES = {
    1: "Mesha", 2: "Vrishabha", 3: "Mithuna", 4: "Karka", 
    5: "Simha", 6: "Kanya", 7: "Tula", 8: "Vrischika", 
    9: "Dhanu", 10: "Makara", 11: "Kumbha", 12: "Meena"
}

# Aligned with the Vedic Graha naming standards
SIGN_LORDS = {
    1: "Mangala", 2: "Shukra", 3: "Budha", 4: "Chandra", 
    5: "Surya", 6: "Budha", 7: "Shukra", 8: "Mangala", 
    9: "Guru", 10: "Shani", 11: "Shani", 12: "Guru"
}

PLANET_MAP_TRANSLATION = {
    "Sun": "Surya", "Moon": "Chandra", "Mercury": "Budha",
    "Venus": "Shukra", "Mars": "Mangala", "Jupiter": "Guru",
    "Saturn": "Shani", "Rahu": "Rahu", "Ketu": "Ketu"
}

def calculate_swisseph_chart(year, month, day, hour_str, lat, lon):
    """Computes precise Vedic coordinates using Swiss Ephemeris Lahiri Ayanamsha with Sanskrit Rashi names."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    calc_flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    try:
        if ":" in str(hour_str):
            h_part, m_part = map(int, hour_str.split(":"))
        else:
            hour_decimal = float(hour_str)
            h_part = int(hour_decimal)
            m_part = int(round((hour_decimal - h_part) * 60))
    except Exception:
        h_part, m_part = 4, 0

    tz_name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
    try:
        local_dt = datetime(year, month, day, h_part, m_part, 0, tzinfo=ZoneInfo(tz_name))
        raw_offset_seconds = local_dt.utcoffset().total_seconds()
        tz_offset_hours = raw_offset_seconds / 3600.0
    except Exception:
        tz_offset_hours = 5.75

    local_decimal_hours = h_part + (m_part / 60.0)
    ut_decimal_hours = local_decimal_hours - tz_offset_hours

    ut_dt_calc = datetime(year, month, day, 0, 0, 0)
    adjusted_ut_dt = ut_dt_calc + timedelta(hours=ut_decimal_hours)
    
    year_ut = adjusted_ut_dt.year
    month_ut = adjusted_ut_dt.month
    day_ut = adjusted_ut_dt.day
    final_ut_hours = adjusted_ut_dt.hour + (adjusted_ut_dt.minute / 60.0) + (adjusted_ut_dt.second / 3600.0)

    julian_day_ut = swe.julday(year_ut, month_ut, day_ut, final_ut_hours)

    cusps, ascmc = swe.houses_ex(julian_day_ut, lat, lon, b'W', calc_flag)
    asc_deg = ascmc[0] 
    base_asc_sign = int(asc_deg // 30) + 1

    PLANET_IDS = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    planet_map = {i: [] for i in range(1, 13)}

    for name, p_id in PLANET_IDS.items():
        res, ret_flag = swe.calc_ut(julian_day_ut, p_id, calc_flag)
        p_long = res[0]
        planet_sign = int(p_long // 30) + 1
        
        target_house = ((planet_sign - base_asc_sign) % 12) + 1
        vedic_name = PLANET_MAP_TRANSLATION.get(name, name)
        
        # FIXED: Appending the calculated Sanskrit string token instead of the Western key
        planet_map[target_house].append(vedic_name)
        
        if name == "Rahu":
            ketu_sign = ((planet_sign + 6 - 1) % 12) + 1
            ketu_house = ((ketu_sign - base_asc_sign) % 12) + 1
            planet_map[ketu_house].append(PLANET_MAP_TRANSLATION["Ketu"])

    house_details = {}
    for h_num in range(1, 13):
        sign_val = ((base_asc_sign + h_num - 2) % 12) + 1
        is_trine = h_num in [1, 5, 9]
        is_quadrant = h_num in [1, 4, 7, 10]
        
        house_details[h_num] = {
            "sign_id": sign_val,
            "rashi_name": RASHI_NAMES[sign_val],
            "lord": SIGN_LORDS[sign_val],
            "classification": "Trikona (Trine)" if is_trine else ("Kendra (Quadrant)" if is_quadrant else "Dusthana" if h_num in [6,8,12] else "Upachaya")
        }

    return asc_deg, planet_map, house_details, tz_name, tz_offset_hours


def compile_ai_bhava_context(house_number, planet_map, house_details):
    """Compiles local database rules using traditional Sanskrit Rashi nomenclatures for the AI."""
    import sqlite3
    conn = sqlite3.connect('jyotish_core.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT sanskrit_name, significations, karaka_planets, ai_interpretation_framework FROM house_rules WHERE house_number = ?", (house_number,))
    house_row = cursor.fetchone()
    
    cursor.execute("SELECT planet, exalted_sign_id, debilitated_sign_id, ai_dignity_directive FROM planetary_dignities")
    dignity_rows = cursor.fetchall()
    dignity_map = {row[0]: {"exalted": row[1], "debilitated": row[2], "text": row[3]} for row in dignity_rows}
    conn.close()

    live_details = house_details.get(house_number, {})
    current_sign_id = live_details.get('sign_id')
    current_rashi = live_details.get('rashi_name')
    current_lord = live_details.get('lord')
    planets_present = planet_map.get(house_number, [])

    context = f"=== SYSTEM GROUNDING CONTEXT FOR EVALUATING HOUSE {house_number} ===\n"
    if house_row:
        context += f"• Sanskrit Bhava: {house_row[0]}\n"
        context += f"• Life Domains: {house_row[1]}\n"
        context += f"• House Karaka: {house_row[2]}\n"
    
    context += f"• Active Sign ruling this house: {current_rashi} (Rashi ID {current_sign_id})\n"
    context += f"• Lord of this Rashi (House Lord): {current_lord}\n"
    context += f"• Occupying Planets: {', '.join(planets_present) if planets_present else 'None (Empty Bhava)'}\n\n"
    
    if planets_present:
        context += "--- LIVE DIGNITY ASSESSMENT ---\n"
        for p in planets_present:
            if p in dignity_map:
                if current_sign_id == dignity_map[p]["exalted"]:
                    context += f"• [DIGNITY] {p} is EXALTED in {current_rashi}: {dignity_map[p]['text']}\n"
                elif current_sign_id == dignity_map[p]["debilitated"]:
                    context += f"• [DIGNITY] {p} is DEBILITATED in {current_rashi}: {dignity_map[p]['text']}\n"
                    
    return context

# ==============================================================================
# CORE VIEW ROUTES
# ==============================================================================

@app.route('/')
def home():
    asc_deg, planet_map, house_details, tz_name, tz_offset = calculate_swisseph_chart(1992, 12, 17, "04:55", 26.4525, 87.2718)
    return render_template('index.html', asc_deg=asc_deg, planet_map=planet_map, house_details=house_details, tz_name=tz_name, tz_offset=tz_offset)


@app.route('/database-explorer')
def database_explorer_page():
    return render_template('db_explorer.html')

# ==============================================================================
# CORE API ENDPOINTS
# ==============================================================================

@app.route('/api/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json() or {}
        place_name = data.get('place', '').strip()
        year = int(data.get('year', 1992))
        month = int(data.get('month', 12))
        day = int(data.get('day', 17))
        time_str = data.get('time', '04:55')

        display_place = "Unknown Location"

        if place_name:
            location = geolocator.geocode(place_name, addressdetails=True)
            if location:
                lat = location.latitude
                lon = location.longitude
                address_dict = location.raw.get('address', {})
                display_place = address_dict.get('city') or address_dict.get('town') or place_name.capitalize()
            else:
                return jsonify({"status": "error", "message": f"Could not resolve location: '{place_name}'"}), 400
        else:
            lat = float(data.get('lat', 26.4525))
            lon = float(data.get('lon', 87.2718))
            display_place = "Biratnagar"
        
        asc_deg, planet_map, house_details, tz_name, tz_offset = calculate_swisseph_chart(year, month, day, time_str, lat, lon)
        
        return jsonify({
            "status": "success",
            "asc_deg": asc_deg,
            "planet_map": planet_map,
            "house_details": house_details,
            "tz_name": tz_name,
            "display_place": display_place,
            "tz_offset": tz_offset,
            "resolved_lat": lat,
            "resolved_lon": lon
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/api/house/<int:house_num>')
def house_details(house_num):
    try:
        asc_deg, planet_map, house_details, tz_name, tz_offset = calculate_swisseph_chart(1992, 12, 17, "04:55", 26.4525, 87.2718)
        structured_context = compile_ai_bhava_context(house_num, planet_map, house_details)
        ai_response = run_direct_astrology_analysis(structured_context)
        return jsonify({"status": "success", "ai_interpretation": ai_response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/db/schema', methods=['GET'])
def get_database_schema():
    try:
        import sqlite3
        conn = sqlite3.connect('jyotish_core.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        conn.close()
        return jsonify({"status": "success", "tables": tables})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/db/table-data', methods=['GET'])
def get_table_data():
    try:
        table_name = request.args.get('table', '').strip()
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(1, int(request.args.get('limit', 10)))
        
        if not table_name:
            return jsonify({"status": "error", "message": "No table name provided"}), 400

        import sqlite3
        conn = sqlite3.connect('jyotish_core.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]

        offset = (page - 1) * per_page
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")
        raw_rows = cursor.fetchall()
        rows = [dict(row) for row in raw_rows]
        conn.close()

        import math
        total_pages = max(1, math.ceil(total_rows / per_page))

        return jsonify({
            "status": "success",
            "table": table_name,
            "columns": columns,
            "rows": rows,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total_rows": total_rows,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)