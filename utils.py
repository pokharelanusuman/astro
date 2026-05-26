# Decorators and utilities for response handling and error management
from functools import wraps
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """Standardized API response wrapper"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Return a success response"""
        response = {
            "status": "success",
            "message": message,
            "data": data
        }
        return jsonify(response), status_code

    @staticmethod
    def error(message="Error", status_code=400, error_code=None):
        """Return an error response"""
        response = {
            "status": "error",
            "message": message,
        }
        if error_code:
            response["error_code"] = error_code
        return jsonify(response), status_code

    @staticmethod
    def created(data=None, message="Resource created"):
        """Return a created response"""
        return APIResponse.success(data, message, 201)

    @staticmethod
    def not_found(message="Resource not found"):
        """Return a not found response"""
        return APIResponse.error(message, 404, "NOT_FOUND")

    @staticmethod
    def bad_request(message="Invalid request"):
        """Return a bad request response"""
        return APIResponse.error(message, 400, "BAD_REQUEST")

    @staticmethod
    def server_error(message="Internal server error"):
        """Return a server error response"""
        return APIResponse.error(message, 500, "SERVER_ERROR")


def handle_errors(func):
    """Decorator to handle common errors in API routes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return APIResponse.bad_request(str(e))
        except KeyError as e:
            logger.warning(f"Missing key in {func.__name__}: {str(e)}")
            return APIResponse.bad_request(f"Missing required parameter: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return APIResponse.server_error(str(e))
    return wrapper


def require_json(*required_fields):
    """Decorator to validate JSON request and required fields"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                return APIResponse.bad_request("Request must be JSON")
            
            data = request.get_json()
            
            for field in required_fields:
                if field not in data or data[field] is None:
                    return APIResponse.bad_request(f"Missing required field: {field}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_request(func):
    """Decorator to log incoming requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        logger.info(f"{request.method} {request.path} - IP: {request.remote_addr}")
        return func(*args, **kwargs)
    return wrapper
