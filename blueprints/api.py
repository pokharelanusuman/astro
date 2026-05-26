# API Routes Blueprint
from flask import Blueprint, request
from utils import APIResponse, handle_errors, require_json, log_request
from services.chart_service import ChartCalculationService
from services.db_service import DatabaseService
from services.ai_service import AIAnalysisService

api_bp = Blueprint('api', __name__, url_prefix='/api')
chart_service = ChartCalculationService()
db_service = DatabaseService()
ai_service = AIAnalysisService()


@api_bp.route('/health', methods=['GET'])
@log_request
def health_check():
    """Health check endpoint"""
    return APIResponse.success({
        "status": "healthy",
        "ai_available": ai_service.is_available()
    })


@api_bp.route('/calculate', methods=['POST'])
@log_request
@handle_errors
@require_json('year', 'month', 'day', 'hour', 'latitude', 'longitude')
def calculate_chart():
    """Calculate a Vedic astrology chart"""
    data = request.get_json()
    
    try:
        # Validate input
        year = int(data['year'])
        month = int(data['month'])
        day = int(data['day'])
        hour = data['hour']
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        
        # Validate ranges
        if not (1 <= month <= 12) or not (1 <= day <= 31):
            raise ValueError("Invalid month or day")
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise ValueError("Invalid coordinates")
        
        # Calculate chart
        chart = chart_service.calculate_chart(year, month, day, hour, lat, lon)
        
        # Get location string
        location = chart_service.get_location_string(lat, lon)
        
        # Add metadata
        chart['location'] = location
        chart['birth_data'] = {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'latitude': lat,
            'longitude': lon
        }
        
        return APIResponse.success(chart, "Chart calculated successfully")
        
    except ValueError as e:
        return APIResponse.bad_request(f"Invalid input: {str(e)}")


@api_bp.route('/analyze', methods=['POST'])
@log_request
@handle_errors
@require_json('chart_data')
def analyze_chart():
    """Get AI-powered analysis of a chart"""
    data = request.get_json()
    
    try:
        chart_data = data['chart_data']
        
        # Format chart data for AI
        context = _format_chart_for_analysis(chart_data)
        
        # Get analysis
        analysis = ai_service.analyze_chart(context)
        
        return APIResponse.success({
            "analysis": analysis,
            "model": ai_service.model,
            "ai_available": True
        })
        
    except Exception as e:
        return APIResponse.bad_request(f"Analysis failed: {str(e)}")


@api_bp.route('/db/schema', methods=['GET'])
@log_request
@handle_errors
def get_db_schema():
    """Get database schema"""
    try:
        schema = db_service.get_schema()
        return APIResponse.success({
            "tables": list(schema.keys()),
            "schema": schema
        })
    except Exception as e:
        return APIResponse.server_error(f"Failed to retrieve schema: {str(e)}")


@api_bp.route('/db/table/<table_name>', methods=['GET'])
@log_request
@handle_errors
def get_table_data(table_name):
    """Get data from a specific table with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        if page < 1 or limit < 1 or limit > 1000:
            return APIResponse.bad_request("Invalid page or limit")
        
        offset = (page - 1) * limit
        
        result = db_service.get_table_data(table_name, limit, offset)
        
        total_pages = (result['total'] + limit - 1) // limit
        
        return APIResponse.success({
            "table": table_name,
            "data": result['data'],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": result['total'],
                "total_pages": total_pages
            }
        })
    except ValueError as e:
        return APIResponse.bad_request(str(e))
    except Exception as e:
        return APIResponse.server_error(f"Failed to retrieve table data: {str(e)}")


@api_bp.route('/house/<int:house_num>', methods=['GET'])
@log_request
@handle_errors
def get_house_info(house_num):
    """Get information about a specific house"""
    from constants import HOUSE_NAMES
    
    if house_num < 1 or house_num > 12:
        return APIResponse.bad_request("House number must be between 1 and 12")
    
    house_info = {
        "house_number": house_num,
        "name": HOUSE_NAMES.get(house_num, "Unknown"),
        "description": f"House {house_num} significance and interpretation"
    }
    
    return APIResponse.success(house_info)


@api_bp.route('/knowledge-state', methods=['GET'])
@log_request
@handle_errors
def get_knowledge_state():
    """Get current AI knowledge base state"""
    try:
        from knowledge_manager import get_all_learning_insights
        
        insights = get_all_learning_insights()
        
        return APIResponse.success({
            "insights_count": len(insights) if insights else 0,
            "ai_learning_enabled": True
        })
    except Exception as e:
        return APIResponse.server_error(f"Failed to retrieve knowledge state: {str(e)}")


def _format_chart_for_analysis(chart_data):
    """Format chart data into a human-readable string for AI analysis"""
    lines = [
        "=== VEDIC ASTROLOGY CHART DATA ===",
        "",
        f"Ascendant: {chart_data.get('ascendant_rashi', 'Unknown')} ({chart_data.get('ascendant_degree', 0):.2f}°)",
        "",
        "PLANETARY POSITIONS:",
    ]
    
    planets = chart_data.get('planets', {})
    for planet_name, planet_data in planets.items():
        lines.append(
            f"  {planet_name}: {planet_data.get('rashi', 'Unknown')} "
            f"({planet_data.get('rashi_degree', 0):.2f}°)"
        )
    
    lines.append("")
    lines.append("HOUSE PLACEMENTS:")
    
    house_mapping = chart_data.get('house_mapping', {})
    for house_num in range(1, 13):
        planets_in_house = house_mapping.get(house_num, [])
        planets_str = ", ".join(planets_in_house) if planets_in_house else "Empty"
        lines.append(f"  House {house_num}: {planets_str}")
    
    return "\n".join(lines)
