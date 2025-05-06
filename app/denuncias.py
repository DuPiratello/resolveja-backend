from flask import Blueprint, jsonify, request  # type: ignore
from app import db
from app.models import Denuncia
from flask_cors import CORS # type: ignore

denuncia_bp = Blueprint('denuncia', __name__)
CORS(denuncia_bp, resources={r"/*": {"origins": "*"}})

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
    # Use request.get_json() para acessar os dados enviados como JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Nenhum dado foi enviado"}), 400

    titulo = data.get('titulo')
    tipo = data.get('tipo')
    status = data.get('status', 'Pendente')  # Valor padrão para status

    # Verifique se os campos obrigatórios estão presentes
    if not titulo or not tipo:
        return jsonify({"error": "Campos 'titulo' e 'tipo' são obrigatórios"}), 400

    # Crie a nova denúncia
    nova_denuncia = Denuncia(
        titulo=titulo,
        tipo=tipo,
        status=status
    )

    db.session.add(nova_denuncia)
    db.session.commit()

    return jsonify({
        "message": "Denúncia criada com sucesso!",
        "id": nova_denuncia.id
    }), 201
