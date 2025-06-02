from flask import Blueprint, jsonify, request, current_app, send_from_directory  # type:ignore
from flask_jwt_extended import jwt_required, get_jwt_identity  # type:ignore
from app.decorators import role_required
from app import db
from app.models import Denuncia
from app.models import User
import os
from werkzeug.utils import secure_filename # type:ignore

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

@admin_routes.route('/', methods=['GET'])
@jwt_required()
@role_required("admin")
def admin_panel():
    return jsonify({"message": "Bem-vindo, Admin!"})

@denuncia_routes.route('/denuncias', methods=['GET'])
def get_denuncias():
    denuncias = Denuncia.query.all()
    return jsonify([
        {'id': d.id,
         'titulo': d.titulo,
         'tipo': d.tipo,
         'status': d.status,
         'fotoUrl': getattr(d.user, 'fotoUrl', None)}
        for d in denuncias
    ])

@denuncia_routes.route('/denuncias', methods=['POST'])
@jwt_required()
def create_denuncia():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    if not data or not all(key in data for key in ['titulo', 'tipo']):
        return jsonify({"error": "Campos 'titulo' e 'tipo' são obrigatórios"}), 400

    nova_denuncia = Denuncia(
        titulo=data['titulo'],
        tipo=data['tipo'],
        user_id=current_user_id,
        status=data.get('status', 'Pendente'),
        endereco=data.get('endereco'),
        descricao=data.get('descricao')
    )

    db.session.add(nova_denuncia)
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

@main.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
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