from flask import Blueprint, jsonify, request, current_app, send_from_directory  # type:ignore
from flask_jwt_extended import jwt_required, get_jwt_identity  # type:ignore
from app.decorators import role_required
from app import db
from app.models import Denuncia
from app.models import User
import os
from werkzeug.utils import secure_filename # type:ignore
import uuid
from sqlalchemy import func  # type:ignore

# Definição do blueprint 'main'
main = Blueprint('main', __name__)

# Configurações de upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Garante que a pasta de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def home():
    return jsonify({"message": "API rodando!"})

# Definição do blueprint 'admin_routes'
admin_routes = Blueprint('admin_routes', __name__)
denuncia_routes = Blueprint('denuncia_routes', __name__)


@denuncia_routes.route('/denuncias', methods=['GET'])
def get_denuncias():
    """
    Cria uma nova denúncia
    ---
    tags:
      - Denúncias
    consumes:
      - multipart/form-data
    parameters:
      - name: titulo
        in: formData
        type: string
        required: true
      - name: tipo
        in: formData
        type: string
        required: true
      - name: status
        in: formData
        type: string
      - name: endereco
        in: formData
        type: string
      - name: descricao
        in: formData
        type: string
      - name: foto
        in: formData
        type: file
    responses:
      201:
        description: Denúncia criada com sucesso
    """
    denuncias = Denuncia.query.all()
    return jsonify([
        {
            'id': d.id,
            'titulo': d.titulo,
            'tipo': d.tipo,
            'status': d.status,
            'descricao': d.descricao,
            'endereco': d.endereco,
            'fotoUrl': getattr(d.user, 'fotoUrl', None),
            'reportFotoUrl': d.reportFotoUrl,
            'usuario': {
                'id': d.user.id if d.user else None,
                'username': d.user.username if d.user else None
            } if d.user else None
        }
        for d in denuncias
    ])

@denuncia_routes.route('/denuncias', methods=['POST'])
@jwt_required()
def create_denuncia():
    """
    Lista as denúncias do usuário autenticado
    ---
    tags:
      - Denúncias
    responses:
      200:
        description: Lista de denúncias do usuário
        schema:
          type: array
          items:
            $ref: '#/definitions/Denuncia'
    """
    current_user_id = get_jwt_identity()

    # Recebe campos de texto do form
    titulo = request.form.get('titulo')
    tipo = request.form.get('tipo')
    status = request.form.get('status', 'Pendente')
    endereco = request.form.get('endereco')
    descricao = request.form.get('descricao')

    if not titulo or not tipo:
        return jsonify({"error": "Campos 'titulo' e 'tipo' são obrigatórios"}), 400

    # Cria a denúncia sem foto primeiro
    nova_denuncia = Denuncia(
        titulo=titulo,
        tipo=tipo,
        user_id=current_user_id,
        status=status,
        endereco=endereco,
        descricao=descricao,
        reportFotoUrl=None
    )
    db.session.add(nova_denuncia)
    db.session.commit()

    # Agora salva a foto, se houver, usando o id da denúncia + uuid
    foto = request.files.get('foto')
    if foto and foto.filename != '':
        if not allowed_file(foto.filename):
            return jsonify({"error": "Formato de arquivo não permitido"}), 400
        ext = foto.filename.rsplit('.', 1)[1].lower()
        unique_id = uuid.uuid4().hex
        filename = secure_filename(f"denuncia_{nova_denuncia.id}_{unique_id}.{ext}")
        caminho = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(caminho)
        foto_url = f'/assets/uploads/{filename}'
        nova_denuncia.reportFotoUrl = foto_url
        db.session.commit()

    return jsonify({
        "message": "Denuncia criada com sucesso!",
        "id": nova_denuncia.id
    }), 201

@denuncia_routes.route('/minhas-denuncias', methods=['GET'])
@jwt_required()
def get_minhas_denuncias():
    current_user_id = get_jwt_identity()
    denuncias = Denuncia.query.filter_by(user_id=current_user_id).all()
    return jsonify([
        {
            'id': d.id,
            'titulo': d.titulo,
            'tipo': d.tipo,
            'status': d.status,
            'descricao': d.descricao,
            'fotoUrl': getattr(d.user, 'fotoUrl', None)
        } for d in denuncias
    ])

@denuncia_routes.route('/denuncias/<int:id>', methods=['PUT', 'OPTIONS'])
@jwt_required()
@role_required('admin')  # Ou remova se quiser permitir para outros perfis
def update_denuncia(id):
    """
    Atualiza uma denúncia existente
    ---
    tags:
      - Denúncias
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        schema:
          $ref: '#/definitions/Denuncia'
    responses:
      200:
        description: Denúncia atualizada com sucesso
    """
    denuncia = Denuncia.query.get(id)
    if not denuncia:
        return jsonify({'error': 'Denúncia não encontrada'}), 404

    data = request.get_json()
    if 'status' in data:
        denuncia.status = data['status']
    if 'titulo' in data:
        denuncia.titulo = data['titulo']
    if 'descricao' in data:
        denuncia.descricao = data['descricao']
    if 'tipo' in data:
        denuncia.tipo = data['tipo']
    if 'endereco' in data:
        denuncia.endereco = data['endereco']

    db.session.commit()
    return jsonify({'message': 'Denúncia atualizada com sucesso!'})

@denuncia_routes.route('/coordenadas', methods=['GET'])
def get_coordenadas():
    """
    Lista coordenadas de todas as denúncias
    ---
    tags:
      - Denúncias
    responses:
      200:
        description: Lista de coordenadas
        schema:
          type: array
          items:
            type: array
            items:
              type: number
    """
    denuncias = Denuncia.query.with_entities(Denuncia.endereco).all()
    coordenadas = []

    for denuncia in denuncias:
        if denuncia.endereco:
            try:
                lat, lng = map(float, denuncia.endereco.split(','))
                coordenadas.append([lat, lng, 0.5])
            except ValueError:
                continue

    return jsonify(coordenadas)

@denuncia_routes.route('/coordenadas-ativas', methods=['GET'])
def get_coordenadas_ativas():
    """
    Lista coordenadas de denúncias ativas (não resolvidas/canceladas)
    ---
    tags:
      - Denúncias
    responses:
      200:
        description: Lista de coordenadas ativas
        schema:
          type: array
          items:
            type: array
            items:
              type: number
    """
    try:
        # Buscar apenas denúncias que não estão resolvidas nem canceladas
        denuncias = Denuncia.query.filter(
            ~Denuncia.status.in_(['Resolvido', 'Cancelado', 'resolvido', 'cancelado'])
        ).all()
        
        coordenadas = []
        for denuncia in denuncias:
            if denuncia.endereco:
                try:
                    lat, lng = map(float, denuncia.endereco.split(','))
                    # Formato [latitude, longitude, intensidade]
                    coordenadas.append([
                        float(lat),
                        float(lng), 
                        1.0  # intensidade padrão
                    ])
                except ValueError:
                    continue
        
        return jsonify(coordenadas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@denuncia_routes.route('/leaderboard', methods=['GET'])
def leaderboard():
    """
    Retorna o ranking dos usuários com mais denúncias resolvidas
    ---
    tags:
      - Denúncias
    responses:
      200:
        description: Ranking de usuários
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              username:
                type: string
              resolvidas:
                type: integer
    """
    from .models import User, Denuncia

    # Consulta: top 5 usuários com mais denúncias resolvidas
    results = (
        db.session.query(
            User.id,
            User.username,
            func.count(Denuncia.id).label('resolvidas')
        )
        .join(Denuncia, Denuncia.user_id == User.id)
        .filter(Denuncia.status.ilike('resolvido'))
        .group_by(User.id, User.username)
        .order_by(func.count(Denuncia.id).desc())
        .limit(5)
        .all()
    )

    leaderboard = [
        {"id": r.id, "username": r.username, "resolvidas": r.resolvidas}
        for r in results
    ]
    return jsonify(leaderboard)

@main.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    """
    Retorna os dados de um usuário pelo ID
    ---
    tags:
      - Usuários
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dados do usuário
        schema:
          type: object
          properties:
            id:
              type: integer
            username:
              type: string
            email:
              type: string
            role:
              type: string
            telefone:
              type: string
            fotoUrl:
              type: string
      404:
        description: Usuário não encontrado
    """
    usuario = User.query.get(id)
    if usuario:
        return jsonify({
            "id": usuario.id,
            "username": getattr(usuario, "username", None),
            "email": getattr(usuario, "email", None),
            "role": getattr(usuario, "role", None),
            "telefone": getattr(usuario, "phone", None),
            "fotoUrl": getattr(usuario, "fotoUrl", None)
        })
    return jsonify({"error": "Usuário não encontrado"}), 404

@main.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_usuario(id):
    """
    Atualiza dados do usuário (telefone e foto)
    ---
    tags:
      - Usuários
    consumes:
      - multipart/form-data
    parameters:
      - name: id
        in: path
        type: integer
        required: true
      - name: telefone
        in: formData
        type: string
      - name: foto
        in: formData
        type: file
    responses:
      200:
        description: Usuário atualizado
      404:
        description: Usuário não encontrado
    """
    usuario = User.query.get(id)  # Corrigido: User em vez de usuario
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    telefone = request.form.get('telefone')
    if telefone:
        usuario.telefone = telefone

    if 'foto' in request.files:
        foto = request.files['foto']
        if foto.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado"}), 400
        
        if not allowed_file(foto.filename):
            return jsonify({"error": "Formato de arquivo não permitido"}), 400

        filename = secure_filename(f"user_{id}_{foto.filename}")
        caminho = os.path.join(UPLOAD_FOLDER, filename)
        foto.save(caminho)
        usuario.fotoUrl = f'/assets/uploads/{filename}'

    db.session.commit()
    return jsonify({
        "id": usuario.id,
        "telefone": getattr(usuario, 'telefone', None),
        "fotoUrl": getattr(usuario, 'fotoUrl', None)
    })

# Rota para servir arquivos estáticos
@main.route('/assets/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def register_routes(app):
    app.register_blueprint(main)
    app.register_blueprint(admin_routes, url_prefix='/admin')
    app.register_blueprint(denuncia_routes, url_prefix='/api')
    # Configura a pasta de upload no app
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER