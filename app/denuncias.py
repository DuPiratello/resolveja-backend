from flask import Blueprint, jsonify, request  # type: ignore
from app import db
from app.models import Denuncia

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

@denuncia_bp.route('/denuncias', methods=['POST'])
def create_denuncia():
    data = request.get_json()
    
    if not data or not all(key in data for key in ['titulo', 'tipo']):
        return jsonify({"error": "Campos 'titulo' e 'tipo' são obrigatórios"}), 400

    nova_denuncia = Denuncia(
        titulo=data['titulo'],
        tipo=data['tipo'],
        status=data.get('status', 'Pendente')  # Usa 'Pendente' se o status não for informado
    )

    db.session.add(nova_denuncia)
    db.session.commit()

    return jsonify({
        "message": "Denúncia criada com sucesso!",
        "id": nova_denuncia.id
    }), 201
