# Web Routes Blueprint (HTML pages)
from flask import Blueprint, render_template
from vedic_data_service import get_vedic_data_service

web_bp = Blueprint('web', __name__)


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
            planet_map=planet_map
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
