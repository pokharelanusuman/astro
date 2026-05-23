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
# ENHANCED DEFENSIVE PROCESS GUARD RAILS (Fixes Semaphore Leaks)
# ==============================================================================
def graceful_shutdown_handler(signum, frame):
    """
    Interceptions signal terminations (Ctrl+C). Forcefully kills orphan background 
    CrewAI multiprocess workers and silences tracking resource garbage collections.
    """
    # 1. Silence the noisy resource_tracker warnings right before exiting
    warnings.filterwarnings("ignore", category=UserWarning, module="multiprocessing.resource_tracker")
    
    try:
        current_process = psutil.Process(os.getpid())
        # Find all background children processes spawned by CrewAI/LiteLLM
        children = current_process.children(recursive=True)
        
        for child in children:
            try:
                # Do not disrupt the resource tracker while it's attempting to unwind
                if "resource_tracker" in child.name(): 
                    continue
                child.terminate()  # Terminate worker cleanly
            except (psutil.NoSuchProcess, psutil.AccessDenied): 
                pass
                
        # Wait briefly for standard background process de-allocations
        psutil.wait_procs(children, timeout=0.5)
    except Exception: 
        pass
    
    # Exit with a standard success flag
    os._exit(0)

# Bind system interruption calls directly to our process interceptor sweep
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)