# Web Routes Blueprint (HTML pages)
from flask import Blueprint, render_template
from vedic_data_service import get_vedic_data_service
from services.chart_service import ChartCalculationService
from config import get_config

config = get_config()
web_bp = Blueprint('web', __name__)
# Initialize chart service with default zodiac mode from config
chart_service = ChartCalculationService(zodiac_mode=config.ZODIAC_MODE)


@web_bp.route('/')
def index():
    """Home page"""
    try:
        # Load all Vedic data from database
        vds = get_vedic_data_service()
        
        # Get all reference data
        planets = vds.get_all_planets()
        rashis = vds.get_all_rashis()
        nakshatras = vds.get_all_nakshatras()
        houses = vds.get_all_houses()
        
        # Create planet map for JavaScript
        planet_map = {p['name']: {'id': p['planet_id'], 'name': p['name'], 'sanskrit_name': p['sanskrit_name']} for p in planets}
        
        # Default homepage chart values
        default_chart = {
            'year': 1992,
            'month': 12,
            'day': 17,
            'time': '04:00',
            'place': 'Kathmandu'
        }

        # Build an initial chart payload for first page load
        initial_chart_payload = {}
        lat, lon = chart_service.get_coordinates_from_place(default_chart['place'])
        if lat is not None and lon is not None:
            chart_payload = chart_service.calculate_chart(
                default_chart['year'],
                default_chart['month'],
                default_chart['day'],
                default_chart['time'],
                lat,
                lon
            )
            chart_payload['location'] = chart_service.get_location_string(lat, lon)
            chart_payload['birth_data'] = {
                'year': default_chart['year'],
                'month': default_chart['month'],
                'day': default_chart['day'],
                'hour': default_chart['time'],
                'latitude': lat,
                'longitude': lon
            }

            house_details_payload = {}
            for i, cusp in enumerate(chart_payload['cusps'], start=1):
                rashi = vds.get_rashi_from_degree(cusp)
                house_info = next((h for h in houses if h['house_number'] == i), {})
                house_details_payload[i] = {
                    'rashi_name': rashi['name'] if rashi else 'Unknown',
                    'classification': house_info.get('name', f'House {i}'),
                    'lord': rashi.get('lord_planet_name') if rashi else 'Unknown'
                }
            chart_payload['house_details'] = house_details_payload
            chart_payload['planet_map'] = {str(k): v for k, v in chart_payload['house_mapping'].items()}
            initial_chart_payload = chart_payload

        # Create house details - this is for the initial page load template
        # It should contain basic house information
        house_details = {}
        for h in houses:
            house_details[h['house_number']] = {
                'house_number': h['house_number'],
                'name': h['name'],
                'significations': h['significations'] or 'Not available',
                'karaka_planets': h['karaka_planets'] or 'Not available',
                'positive_traits': h['positive_traits'] or 'Not available',
                'negative_traits': h['negative_traits'] or 'Not available',
            }
        
        return render_template(
            'index.html',
            planets=planets,
            rashis=rashis,
            nakshatras=nakshatras,
            houses=houses,
            house_details=house_details,
            planet_map=planet_map,
            default_chart=default_chart,
            initial_chart_payload=initial_chart_payload
        )
    except Exception as e:
        import logging
        logging.error(f"Error in index route: {e}", exc_info=True)
        return f"Error loading page: {e}", 500


@web_bp.route('/database-explorer')
def database_explorer():
    """Database explorer interface"""
    try:
        # Load all Vedic data from database
        vds = get_vedic_data_service()
        
        # Get all reference data
        planets = vds.get_all_planets()
        rashis = vds.get_all_rashis()
        nakshatras = vds.get_all_nakshatras()
        houses = vds.get_all_houses()
        dignities = vds.get_all_planetary_dignities()
        
        # Create planet map for JavaScript
        planet_map = {p['name']: {'id': p['planet_id'], 'name': p['name'], 'sanskrit_name': p['sanskrit_name']} for p in planets}
        
        # Create house details
        house_details = {}
        for h in houses:
            house_details[h['house_number']] = {
                'house_number': h['house_number'],
                'name': h['name'],
                'significations': h['significations'] or 'Not available',
                'karaka_planets': h['karaka_planets'] or 'Not available',
                'positive_traits': h['positive_traits'] or 'Not available',
                'negative_traits': h['negative_traits'] or 'Not available',
            }
        
        return render_template(
            'db_explorer.html',
            planets=planets,
            rashis=rashis,
            nakshatras=nakshatras,
            houses=houses,
            house_details=house_details,
            planet_map=planet_map,
            dignities=dignities
        )
    except Exception as e:
        import logging
        logging.error(f"Error in database_explorer route: {e}", exc_info=True)
        return f"Error loading page: {e}", 500
