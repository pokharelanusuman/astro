@app.route('/api/calculate', methods=['POST'])
def api_calculate_custom_chart():
    """Endpoint to handle input coordinates from the frontend form."""
    try:
        data = request.json
        year = int(data.get('year'))
        month = int(data.get('month'))
        day = int(data.get('day'))
        hour = int(data.get('hour'))
        minute = int(data.get('minute'))
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        
        # Hardcode 4.0 offset for Dubai calculations, or pull dynamically if needed
        compute_chart_state(year, month, day, hour, minute, lat, lon, timezone_offset=4.0)
        
        return jsonify({
            'status': 'success',
            'asc_deg': ASCENDANT_DEGREE,
            'planet_map': CURRENT_PLANET_MAP
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Calculation failure: {str(e)}"}), 400