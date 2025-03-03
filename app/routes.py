from flask import Blueprint, jsonify  # type:ignore
from flask_jwt_extended import jwt_required  # type:ignore
from app.decorators import role_required

# Definição do blueprint 'main'
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({"message": "API rodando!"})

# Definição do blueprint 'admin_routes'
admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/', methods=['GET'])
@jwt_required()
@role_required("admin")
def admin_panel():
    return jsonify({"message": "Bem-vindo, Admin!"})
