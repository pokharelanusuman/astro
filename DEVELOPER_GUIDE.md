# 👨‍💼 Developer Guide - Refactored Architecture

## Quick Start for Developers

### Understanding the Structure

```
astro/
├── app.py                    # Flask entry point (95 lines)
├── config.py                 # Configuration management
├── constants.py              # Centralized data & constants
├── utils.py                  # Common utilities & decorators
├── services/                 # Business logic layer
│   ├── chart_service.py      # Chart calculations
│   ├── db_service.py         # Database operations
│   └── ai_service.py         # AI/LLM operations
├── blueprints/               # Route organization
│   ├── api.py                # API routes (/api/*)
│   └── web.py                # Web routes (/, /database-explorer)
└── templates/                # HTML templates
```

### Adding a New Feature

#### 1. Add to Constants (if needed)
```python
# constants.py
NEW_CONSTANT = "value"
```

#### 2. Create a Service
```python
# services/my_service.py
class MyService:
    def __init__(self):
        pass
    
    def my_method(self, data):
        """Do something useful"""
        return result
```

#### 3. Add Routes to API Blueprint
```python
# blueprints/api.py
from services.my_service import MyService

my_service = MyService()

@api_bp.route('/my-endpoint', methods=['POST'])
@handle_errors
@require_json('field1', 'field2')
def my_route():
    data = request.get_json()
    result = my_service.my_method(data)
    return APIResponse.success(result)
```

### Using Services

#### ChartCalculationService
```python
from services.chart_service import ChartCalculationService

service = ChartCalculationService()

# Calculate chart
chart = service.calculate_chart(
    year=1992,
    month=12,
    day=17,
    hour_str="04:55",
    lat=26.4525,
    lon=87.2718
)

print(chart["ascendant_degree"])
print(chart["planets"])
print(chart["house_mapping"])
```

#### DatabaseService
```python
from services.db_service import DatabaseService

service = DatabaseService()

# Get schema
schema = service.get_schema()

# Get table data
data = service.get_table_data("house_rules", limit=100, offset=0)

# Execute custom query
results = service.execute_query("SELECT * FROM nakshatra_rules")

# Insert data
id = service.execute_insert("INSERT INTO table VALUES (?, ?)", (val1, val2))
```

#### AIAnalysisService
```python
from services.ai_service import AIAnalysisService

service = AIAnalysisService()

# Check availability
if service.is_available():
    analysis = service.analyze_chart(context_string)
    print(analysis)
else:
    print("AI service unavailable")

# Get available models
models = service.get_available_models()
```

### Using Decorators

#### Error Handling
```python
from utils import handle_errors

@handle_errors
def my_route():
    # Any exception is caught and formatted as API response
    raise ValueError("Something went wrong")
    # Returns: {"status": "error", "message": "Something went wrong"}, 400
```

#### JSON Validation
```python
from utils import require_json

@require_json('name', 'email', 'age')
def create_user():
    data = request.get_json()
    # Fields are guaranteed to exist and not be None
    print(data['name'])
```

#### Request Logging
```python
from utils import log_request

@log_request
def my_route():
    # Logs: "GET /path - IP: 127.0.0.1"
    pass
```

#### Combining Decorators
```python
@api_bp.route('/users', methods=['POST'])
@log_request
@handle_errors
@require_json('name', 'email')
def create_user():
    data = request.get_json()
    return APIResponse.success({"id": 1})
```

### API Response Patterns

```python
from utils import APIResponse

# Success response
return APIResponse.success(data, "Operation successful", 200)

# Created response
return APIResponse.created(data, "Resource created")

# Error responses
return APIResponse.bad_request("Invalid input")
return APIResponse.not_found("Resource not found")
return APIResponse.server_error("Internal error")
return APIResponse.error("Custom message", 400, "CUSTOM_CODE")
```

### Working with Configuration

```python
from config import get_config

config = get_config()

# Access configuration
print(config.FLASK_ENV)      # 'development'
print(config.PORT)           # 5001
print(config.OLLAMA_URL)     # 'http://localhost:11434'
print(config.DATABASE_PATH)  # './jyotish_core.db'
print(config.DEBUG)          # True

# Configuration is environment-aware
# Set FLASK_ENV=production to get ProductionConfig
```

### Testing Services

Services are designed to be testable without Flask:

```python
# test_services.py
import unittest
from services.chart_service import ChartCalculationService

class TestChartService(unittest.TestCase):
    def setUp(self):
        self.service = ChartCalculationService()
    
    def test_calculate_chart(self):
        chart = self.service.calculate_chart(1992, 12, 17, "04:55", 26.4525, 87.2718)
        self.assertIn("ascendant_degree", chart)
        self.assertIn("planets", chart)
    
    def test_parse_time(self):
        h, m = self.service._parse_time("14:30")
        self.assertEqual(h, 14)
        self.assertEqual(m, 30)
```

### Common Patterns

#### Validation Pattern
```python
@api_bp.route('/validate', methods=['POST'])
@handle_errors
@require_json('data')
def validate():
    data = request.get_json()
    
    # Validate
    if not data['data']:
        return APIResponse.bad_request("Data cannot be empty")
    
    # Process
    result = process(data['data'])
    
    # Return
    return APIResponse.success(result)
```

#### Service Pattern
```python
# Create service
service = MyService()

# Use service
result = service.do_something(param1, param2)

# Return response
return APIResponse.success(result)
```

#### Error Handling Pattern
```python
try:
    result = expensive_operation()
    return APIResponse.success(result)
except ValueError as e:
    return APIResponse.bad_request(str(e))
except KeyError as e:
    return APIResponse.bad_request(f"Missing: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return APIResponse.server_error()
```

## File Organization Best Practices

### When to Create a New Service
- When you have reusable business logic
- When logic doesn't fit in another service
- When you want to isolate a concern
- When you want to make something testable

### When to Create a New Blueprint
- When you have a group of related routes
- When routes serve a specific purpose (api, admin, etc.)
- When you want to organize code by feature

### Where to Put Code
- **Business logic** → services/
- **Routes** → blueprints/
- **Data/constants** → constants.py
- **Common functions** → utils.py
- **Configuration** → config.py

## Extending the Application

### Add a New Service
```
1. Create services/my_service.py
2. Define MyService class
3. Implement methods
4. Import and use in blueprints
```

### Add a New API Endpoint
```
1. Import service in blueprints/api.py
2. Create @api_bp.route()
3. Add decorators
4. Call service method
5. Return APIResponse
```

### Add a New Page
```
1. Create template in templates/
2. Add route in blueprints/web.py
3. Return render_template()
```

## Troubleshooting

### Import Error: No module named 'services'
- Ensure services/__init__.py exists (it does)
- Run from project root directory

### "Cannot connect to database"
- Check DATABASE_PATH in config
- Ensure database file exists
- Check file permissions

### "AttributeError: config has no attribute..."
- Check constants are exported from config.py
- Use get_config() not direct imports

### "Decorator not working"
- Check decorator order (bottom to top execution)
- Ensure proper function signature
- Check imports are correct

## Performance Considerations

- **Services are stateless** - Create new instances or use class methods
- **Database connections** - DatabaseService handles pooling
- **Caching** - Can be added via decorators
- **Logging** - Use Python logging, not print()

## Security Considerations

- **Input validation** - Use @require_json and validate manually
- **SQL injection** - DatabaseService uses parameterized queries
- **Error messages** - Don't expose internal details
- **Configuration** - Keep .env secure, never commit

## Contributing

1. Follow the structure
2. Use services for business logic
3. Use blueprints for routes
4. Use decorators for common patterns
5. Keep functions small and focused
6. Write docstrings
7. Test thoroughly

---

**Happy coding! The architecture is designed to be developer-friendly.** 🚀
