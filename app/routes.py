from flask import Blueprint, jsonify, request  # type:ignore
from flask_jwt_extended import jwt_required, get_jwt_identity  # type:ignore
from app.decorators import role_required
from app import db
from app.models import Denuncia

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

# 📌 **Novo: Definição do blueprint 'denuncia_routes'**
denuncia_routes = Blueprint('denuncia_routes', __name__)

@denuncia_routes.route('/denuncias', methods=['GET'])
def get_denuncias():
    denuncias = Denuncia.query.all()
    return jsonify([
        {'id': d.id, 'titulo': d.titulo, 'tipo': d.tipo, 'status': d.status}
        for d in denuncias
    ])

@denuncia_routes.route('/denuncias', methods=['POST'])
@jwt_required()  # Adicione esta linha para exigir autenticação
def create_denuncia():
    data = request.get_json()
    current_user_id = get_jwt_identity()  # Obtém o ID do usuário do token JWT
    
    if not data or not all(key in data for key in ['titulo', 'tipo']):
        return jsonify({"error": "Campos 'titulo' e 'tipo' são obrigatórios"}), 400

    nova_denuncia = Denuncia(
        titulo=data['titulo'],
        tipo=data['tipo'],
        user_id=current_user_id,  # Usa o ID do usuário autenticado
        status=data.get('status', 'Pendente'),
        endereco=data.get('endereco'),
        descricao=data.get('descricao')  # Campo opcional
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
            'descricao': d.descricao
        } for d in denuncias
    ])

@denuncia_routes.route('/coordenadas', methods=['GET'])
def get_coordenadas():
    denuncias = Denuncia.query.with_entities(Denuncia.endereco).all()
    coordenadas = []

    for denuncia in denuncias:
        if denuncia.endereco:  # Verifica se o campo endereco não é nulo
            try:
                lat, lng = map(float, denuncia.endereco.split(','))
                coordenadas.append([lat, lng, 0.5])  # Adiciona intensidade fixa (ex: 0.5)
            except ValueError:
                continue  # Ignora entradas inválidas

    return jsonify(coordenadas)

# 📌 **Registrar o blueprint na aplicação**
def register_routes(app):
    app.register_blueprint(main)
    app.register_blueprint(admin_routes, url_prefix='/admin')
    app.register_blueprint(denuncia_routes, url_prefix='/api')
