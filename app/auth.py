from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data["username"] == "admin" and data["password"] == "123":
        access_token = create_access_token(identity=data["username"])
        return jsonify(access_token=access_token)
    return jsonify({"error": "Credenciais inválidas"}), 401
