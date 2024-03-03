from functools import wraps
from validation.common import ErrorResponse
from flask import jsonify

def with_error_handling():
    def decorator(callable):

        @wraps(callable)
        def wrapper(*args, **kwargs):
            try:
                return callable(*args, **kwargs)
            except Exception as e:
                print(e, "rrrr")
                return jsonify(ErrorResponse(**{"error": str(e)}).model_dump()), 500

        return wrapper

    return decorator