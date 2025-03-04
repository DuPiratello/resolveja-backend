from flask import Blueprint, jsonify #type: ignore
from app import db
from models import Denuncia

denuncia_bp = Blueprint('denuncia', __name__)

@denuncia_bp.route('/denuncias', methods=['GET'])
def get_denuncias():
    denuncias = Denuncia.query.all()
    return jsonify([{
        'id': d.id,
        'titulo': d.titulo,
        'tipo': d.tipo,
        'status': d.status
    } for d in denuncias])
