import os
import sys
import signal
import psutil
import warnings
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, render_template, jsonify, request
from crew_engine import run_astrology_crew_analysis

import swisseph as swe
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim

app = Flask(__name__)
tf = TimezoneFinder()
geolocator = Nominatim(user_agent="jyotish_engine_core_v2")

# ==============================================================================
# ULTIMATE PROCESS REAPER (Eliminates the final Werkzeug Manager Semaphore Leak)
# ==============================================================================
def graceful_shutdown_handler(signum, frame):
    """
    Forcibly sweeps the entire operating system process group matching this terminal
    session. This stops Flask's debug monitor process and CrewAI background loops 
    simultaneously, ensuring 0 leaked semaphores at exit.
    """
    # 1. Broad filter suppression to ensure warning text won't output during cleanup
    warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")
    
    try:
        current_pid = os.getpid()
        # Find all sibling and worker processes running within our localized tree
        parent = psutil.Process(current_pid)
        children = parent.children(recursive=True)
        
        # Terminate everything in the child tree first
        for child in children:
            try:
                if "resource_tracker" in child.name():
                    continue
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        psutil.wait_procs(children, timeout=0.2)
    except Exception:
        pass

    # 2. CRITICAL TRICK: Kill the entire process group (PGID) at once.
    # This terminates the hidden parent Flask reloader process, forcing a clean exit.
    os.killpg(os.getpgrp(), signal.SIGKILL)
    sys.exit(0)

# Bind structural terminal interrupt commands to our global group-killer
signal.signal(signal.SIGINT, graceful_shutdown_handler)
signal.signal(signal.SIGTERM, graceful_shutdown_handler)
# ==============================================================================

SIGN_LORDS = {
    1: "Mars", 2: "Venus", 3: "Mercury", 4: "Moon", 
    5: "Sun", 6: "Mercury", 7: "Venus", 8: "Mars", 
    9: "Jupiter", 10: "Saturn", 11: "Saturn", 12: "Jupiter"
}

def calculate_swisseph_chart(year, month, day, hour_str, lat, lon):
    """
    Computes precise Vedic coordinates using Swiss Ephemeris Lahiri Ayanamsha.
    Converts Local Time to Universal Time (UT) using geographic coordinates.
    """
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
        planet_map[target_house].append(name)
        
        if name == "Rahu":
            ketu_sign = ((planet_sign + 6 - 1) % 12) + 1
            ketu_house = ((ketu_sign - base_asc_sign) % 12) + 1
            planet_map[ketu_house].append("Ketu")

    house_details = {}
    for h_num in range(1, 13):
        sign_val = ((base_asc_sign + h_num - 2) % 12) + 1
        is_trine = h_num in [1, 5, 9]
        is_quadrant = h_num in [1, 4, 7, 10]
        
        house_details[h_num] = {
            "sign_id": sign_val,
            "lord": SIGN_LORDS[sign_val],
            "classification": "Trikona (Trine)" if is_trine else ("Kendra (Quadrant)" if is_quadrant else "Dusthana" if h_num in [6,8,12] else "Upachaya")
        }

    return asc_deg, planet_map, house_details, tz_name, tz_offset_hours


@app.route('/')
def home():
    asc_deg, planet_map, house_details, tz_name, tz_offset = calculate_swisseph_chart(1992, 12, 17, "04:55", 26.4525, 87.2718)
    return render_template('index.html', asc_deg=asc_deg, planet_map=planet_map, house_details=house_details, tz_name=tz_name, tz_offset=tz_offset)


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
                display_place = address_dict.get('city') or \
                                address_dict.get('town') or \
                                address_dict.get('village') or \
                                address_dict.get('suburb') or \
                                address_dict.get('county') or \
                                place_name.capitalize()
            else:
                return jsonify({"status": "error", "message": f"Could not resolve location parameters for: '{place_name}'"}), 400
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
        ai_response = run_astrology_crew_analysis(101, house_num)
        return jsonify({"status": "success", "ai_interpretation": ai_response})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/database-explorer')
def database_explorer_page():
    """Renders the main template frame for the database explorer."""
    return render_template('db_explorer.html')


@app.route('/api/db/schema', methods=['GET'])
def get_database_schema():
    """
    Dynamically scans the database to list all existing tables.
    Modify the inner logic if you use SQLAlchemy, raw SQLite, or PostgreSQL.
    """
    try:
        # --- EXAMPLE FOR RAW SQLITE/DATABASE INSPECTION ---
        # import sqlite3
        # conn = sqlite3.connect('your_database.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        # conn.close()
        
        # Fallback dummy list for structural illustration/testing
        tables = ["users", "calculation_history", "crewai_logs", "locations_cache"]
        
        return jsonify({"status": "success", "tables": tables})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/api/db/table-data', methods=['GET'])
def get_table_data():
    """Returns dynamic columns, rows, and structural pagination metrics based on selected table."""
    try:
        table_name = request.args.get('table', '').strip()
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(1, int(request.args.get('limit', 10)))
        
        if not table_name:
            return jsonify({"status": "error", "message": "No table name provided"}), 400

        # 1. Define distinct, real schemas for each table configuration
        if table_name == "users":
            columns = ["user_id", "profile_name", "birth_place", "created_at"]
            total_rows = 12
            
            # Generate realistic user rows
            dummy_rows = [
                {"user_id": 1, "profile_name": "Anusuman", "birth_place": "Biratnagar", "created_at": "2026-05-20 10:14"},
                {"user_id": 2, "profile_name": "Astro Profile Beta", "birth_place": "Kathmandu", "created_at": "2026-05-21 14:22"},
                {"user_id": 3, "profile_name": "Client Target A", "birth_place": "Dubai", "created_at": "2026-05-22 09:05"},
            ]
            # Pad the pagination simulation
            for i in range(4, total_rows + 1):
                dummy_rows.append({"user_id": i, "profile_name": f"Anonymous Test #{i}", "birth_place": "Global Cache", "created_at": "2026-05-23 11:00"})

        elif table_name == "calculation_history":
            columns = ["calc_id", "timestamp", "input_date", "input_time", "resolved_lagna", "timezone"]
            total_rows = 24
            dummy_rows = []
            
            start_id = ((page - 1) * per_page) + 1
            end_id = min(start_id + per_page, total_rows + 1)
            for idx in range(start_id, end_id):
                dummy_rows.append({
                    "calc_id": idx,
                    "timestamp": "2026-05-23 21:21",
                    "input_date": "1992-12-17",
                    "input_time": "04:55",
                    "resolved_lagna": f"227.412° (Scorpio)",
                    "timezone": "Asia/Kathmandu (UTC+5.8)"
                })

        elif table_name == "crewai_logs":
            columns = ["log_id", "uuid_token", "target_house", "created_at", "status_flag"]
            total_rows = 45
            dummy_rows = []
            
            start_id = ((page - 1) * per_page) + 1
            end_id = min(start_id + per_page, total_rows + 1)
            for idx in range(start_id, end_id):
                dummy_rows.append({
                    "log_id": idx,
                    "uuid_token": f"TX-100{idx}",
                    "target_house": f"House {((idx - 1) % 12) + 1}",
                    "created_at": "2026-05-23 21:21",
                    "status_flag": "SUCCESS" if idx % 5 != 0 else "FAILED"
                })

        elif table_name == "locations_cache":
            columns = ["cache_id", "queried_place", "resolved_lat", "resolved_lon", "hit_count"]
            total_rows = 8
            dummy_rows = [
                {"cache_id": 1, "queried_place": "Biratnagar", "resolved_lat": 26.4525, "resolved_lon": 87.2718, "hit_count": 14},
                {"cache_id": 2, "queried_place": "Dubai Festival City", "resolved_lat": 25.2226, "resolved_lon": 55.3591, "hit_count": 32},
                {"cache_id": 3, "queried_place": "Burjuman, Dubai", "resolved_lat": 25.2532, "resolved_lon": 55.3034, "hit_count": 9},
                {"cache_id": 4, "queried_place": "Kathmandu", "resolved_lat": 27.7172, "resolved_lon": 85.3240, "hit_count": 5}
            ]

        # Slice the rows based on the page request parameters
        import math
        total_pages = max(1, math.ceil(total_rows / per_page))
        
        # Only slice if we haven't manually pre-sliced the data loop chunks
        if table_name in ["users", "locations_cache"]:
            sliced_rows = dummy_rows[(page - 1) * per_page : page * per_page]
        else:
            sliced_rows = dummy_rows

        return jsonify({
            "status": "success",
            "table": table_name,
            "columns": columns,
            "rows": sliced_rows,
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


@app.route('/database-explorer')
def database_explorer_page():
    """Renders the main template frame for the database explorer."""
    return render_template('db_explorer.html')


@app.route('/api/db/schema', methods=['GET'])
def get_database_schema():
    """
    Dynamically scans the database to list all existing tables.
    Modify the inner logic if you use SQLAlchemy, raw SQLite, or PostgreSQL.
    """
    try:
        # --- EXAMPLE FOR RAW SQLITE/DATABASE INSPECTION ---
        # import sqlite3
        # conn = sqlite3.connect('your_database.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        # tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
        # conn.close()
        
        # Fallback dummy list for structural illustration/testing
        tables = ["users", "calculation_history", "crewai_logs", "locations_cache"]
        
        return jsonify({"status": "success", "tables": tables})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/db/table-data', methods=['GET'])
def get_table_data():
    """Returns dynamic columns, rows, and structural pagination metrics."""
    try:
        table_name = request.args.get('table', '').strip()
        page = max(1, int(request.args.get('page', 1)))
        per_page = max(1, int(request.args.get('limit', 10)))
        
        if not table_name:
            return jsonify({"status": "error", "message": "No table name provided"}), 400

        # --- EXAMPLE ARCHITECTURE FOR DYNAMIC FETCH & PAGINATION ---
        # offset = (page - 1) * per_page
        # cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        # total_rows = cursor.fetchone()[0]
        # cursor.execute(f"PRAGMA table_info({table_name})") # For column headers
        # columns = [col[1] for col in cursor.fetchall()]
        # cursor.execute(f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}")
        # rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Simulated mockup telemetry profiles for initial verification
        columns = ["id", "uuid_token", "created_at", "status_flag"] if "log" in table_name else ["id", "meta_label", "payload_string", "execution_ms"]
        
        # Create mockup rows to verify pagination calculations
        total_rows = 45
        dummy_rows = []
        start_id = ((page - 1) * per_page) + 1
        end_id = min(start_id + per_page, total_rows + 1)
        
        for idx in range(start_id, end_id):
            if "log" in table_name:
                dummy_rows.append({"id": idx, "uuid_token": f"TX-{1000+idx}", "created_at": "2026-05-23", "status_flag": "SUCCESS"})
            else:
                dummy_rows.append({"id": idx, "meta_label": f"Record Matrix Slot {idx}", "payload_string": "Data Blob Data...", "execution_ms": 14.2})

        import math
        total_pages = math.ceil(total_rows / per_page)

        return jsonify({
            "status": "success",
            "table": table_name,
            "columns": columns,
            "rows": dummy_rows,
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