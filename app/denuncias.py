from flask import Blueprint, jsonify, request  # type: ignore
from app import db
from app.models import Denuncia
from flask_cors import CORS # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity #type:ignore  # Adicione no topo do arquivo
from app.decorators import role_required #type:ignore

denuncia_bp = Blueprint('denuncia', __name__)
CORS(denuncia_bp, resources={r"/*": {"origins": "*"}})

@denuncia_bp.route('/denuncias', methods=['GET'])
@jwt_required()
def get_denuncias():
    """
    Lista todas as denúncias
    ---
    tags:
      - Denúncias
    summary: Lista todas as denúncias cadastradas
    description: Retorna uma lista de todas as denúncias registradas no sistema.
    responses:
      200:
        description: Lista de denúncias retornada com sucesso
        schema:
          type: array
          items:
            $ref: '#/definitions/Denuncia'
    """
    denuncias = Denuncia.query.all()
    return jsonify([{
        'id': d.id,
        'titulo': d.titulo,
        'tipo': d.tipo,
        'status': d.status
    } for d in denuncias])

@denuncia_bp.route('/denuncias', methods=['POST'])
@jwt_required()
def create_denuncia():
    """
    Cria uma nova denúncia
    ---
    tags:
      - Denúncias
    summary: Cria uma nova denúncia
    description: Cria uma nova denúncia a partir dos dados enviados no corpo da requisição.
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - titulo
            - tipo
          properties:
            titulo:
              type: string
              description: Título da denúncia
              example: Buraco na rua
            tipo:
              type: string
              description: Tipo da denúncia
              example: Infraestrutura
            status:
              type: string
              description: Status da denúncia
              example: Pendente
            endereco:
              type: string
              description: Endereço da ocorrência
              example: Rua das Flores, 123
            descricao:
              type: string
              description: Descrição detalhada
              example: Há um buraco perigoso na rua X
    responses:
      201:
        description: Denúncia criada com sucesso
        schema:
          $ref: '#/definitions/Denuncia'
      400:
        description: Dados inválidos
      401:
        description: Não autorizado (JWT ausente ou inválido)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Nenhum dado foi enviado"}), 400

    titulo = data.get('titulo')
    tipo = data.get('tipo')
    status = data.get('status', 'Pendente')  # Valor padrão para status
    endereco = data.get('endereco')
    descricao = data.get('descricao')  # Campo opcional

    if not titulo or not tipo:
        return jsonify({"error": "Campos 'titulo' e 'tipo' são obrigatórios"}), 400

    nova_denuncia = Denuncia(
        titulo=titulo,
        tipo=tipo,
        status=status,
        endereco=endereco,
        descricao=descricao
    )

    db.session.add(nova_denuncia)
    db.session.commit()

    return jsonify({
        "message": "Denúncia criada com sucesso!",
        "id": nova_denuncia.id
    }), 201

@denuncia_bp.route('/denuncias/<int:id>', methods=['GET'])
def get_denuncia(id):
    """
    Retorna uma denúncia específica pelo ID
    ---
    tags:
      - Denúncias
    summary: Buscar denúncia por ID
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da denúncia
    responses:
      200:
        description: Detalhes da denúncia
        schema:
          $ref: '#/definitions/Denuncia'
      404:
        description: Denúncia não encontrada
    """
    denuncia = Denuncia.query.get(id)
    if not denuncia:
        return jsonify({"error": "Denúncia não encontrada"}), 404
    return jsonify({
        'id': denuncia.id,
        'titulo': denuncia.titulo,
        'tipo': denuncia.tipo,
        'status': denuncia.status,
        'endereco': denuncia.endereco,
        'descricao': denuncia.descricao
    })

@denuncia_bp.route('/denuncias/<int:id>', methods=['PUT'])
@role_required('admin')
def update_denuncia(id):
    """
    Atualiza uma denúncia existente
    ---
    tags:
      - Denúncias
    summary: Atualizar denúncia por ID
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da denúncia
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            titulo:
              type: string
            tipo:
              type: string
            status:
              type: string
            endereco:
              type: string
            descricao:
              type: string
    responses:
      200:
        description: Denúncia atualizada com sucesso
        schema:
          $ref: '#/definitions/Denuncia'
      400:
        description: Dados inválidos
      404:
        description: Denúncia não encontrada
    """
    denuncia = Denuncia.query.get(id)
    if not denuncia:
        return jsonify({"error": "Denúncia não encontrada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Nenhum dado foi enviado"}), 400

    for field in ['titulo', 'tipo', 'status', 'endereco', 'descricao']:
        if field in data:
            setattr(denuncia, field, data[field])

    db.session.commit()
    return jsonify({"message": "Denúncia atualizada com sucesso!"})

@denuncia_bp.route('/denuncias/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_denuncia(id):
    """
    Remove uma denúncia existente
    ---
    tags:
      - Denúncias
    summary: Remover denúncia por ID
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID da denúncia
    responses:
      204:
        description: Denúncia removida com sucesso
      404:
        description: Denúncia não encontrada
    """
    denuncia = Denuncia.query.get(id)
    if not denuncia:
        return jsonify({"error": "Denúncia não encontrada"}), 404

    db.session.delete(denuncia)
    db.session.commit()
    return '', 204

@denuncia_bp.route('/minhas-denuncias', methods=['GET'])
@jwt_required()
def minhas_denuncias():
    """
    Lista as denúncias do usuário autenticado
    ---
    tags:
      - Denúncias
    summary: Lista denúncias do usuário autenticado
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de denúncias do usuário autenticado
        schema:
          type: array
          items:
            $ref: '#/definitions/Denuncia'
      401:
        description: Não autorizado
    """
    usuario_id = get_jwt_identity()
    denuncias = Denuncia.query.filter_by(usuario_id=usuario_id).all()
    return jsonify([{
        'id': d.id,
        'titulo': d.titulo,
        'tipo': d.tipo,
        'status': d.status,
        'endereco': d.endereco,
        'descricao': d.descricao
    } for d in denuncias])
