from functools import wraps
from flask_jwt_extended import get_jwt_identity #type: ignore
from flask import jsonify #type: ignore
from app.models import User

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or user.role != required_role:
                return jsonify({"error": "Acesso negado"}), 403  # Proibido

            return f(*args, **kwargs)
        return wrapper
    return decorator
