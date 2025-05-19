from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request #type: ignore
from flask import jsonify #type: ignore

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request() # Verifica se o token JWT é válido e se o usuário tem a função necessária
            from app.models import User  # Importa o modelo User aqui para evitar dependências circulares
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or user.role != required_role:
                return jsonify({"error": "Acesso negado"}), 403  # Proibido

            return f(*args, **kwargs)
        return wrapper
    return decorator
