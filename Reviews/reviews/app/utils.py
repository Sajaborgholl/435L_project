from functools import wraps
import jwt
import datetime
from flask import request, jsonify

# Configuration for JWT
JWT_SECRET = "Test"
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600  # Token valid for 1 hour


def generate_jwt(username, user_role):
    """
    Generate a JWT for the given user.

    Args:
        username (str): Username of the user.
        user_role (int): Role of the user (0: Customer, 1: Admin).

    Returns:
        str: JWT token.
    """
    payload = {
        "username": username,
        "user_role": user_role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    return jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)


def decode_jwt(token):
    """
    Decode and validate a JWT.

    Args:
        token (str): JWT token.

    Returns:
        dict: Decoded payload if valid, or an error message.
    """
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def jwt_required(admin_only=False):
    """
    Decorator to protect routes with JWT authentication.

    Args:
        admin_only (bool): If True, requires admin privileges.

    Returns:
        Function: Wrapped route function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return jsonify({"error": "Authorization token is required"}), 401

            token = token.split(" ")[1]  # Remove 'Bearer' prefix
            decoded = decode_jwt(token)

            if "error" in decoded:
                return jsonify(decoded), 401

            if admin_only and decoded.get("user_role") != 1:
                return jsonify({"error": "Admin access required"}), 403

            # Attach decoded payload to request for use in route
            request.user = decoded
            return func(*args, **kwargs)
        return wrapper
    return decorator
