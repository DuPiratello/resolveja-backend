from flask import Flask  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore
from flask_migrate import Migrate  # type: ignore
from flask_socketio import SocketIO  # type: ignore
from flask_cors import CORS  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from config import Config  # Importado antes!
from flasgger import Swagger # type: ignore
from app.decorators import role_required # type: ignore

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=["http://localhost:4200"], 
              supports_credentials=True,
              methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    socketio.init_app(app)

    # ⚠️ Importações de rotas depois da inicialização do db
    from app.routes import main, admin_routes
    from app.auth import auth
    from app.routes import denuncia_routes  # 📌 Importa as rotas de denúncias
    from app.denuncias import denuncia_bp  # 📌 Importa o blueprint de denúncias

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin_routes, url_prefix='/admin')  # Rotas admin
    app.register_blueprint(denuncia_routes, url_prefix='/api')  # 📌 Adiciona as rotas de denúncias
    

    # Configuração detalhada do Swagger
    Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "API de Denúncias - ResolveJá",
            "version": "1.0.0",
            "description": "API para registro, consulta e administração de denúncias públicas.",
            "contact": {
                "name": "Equipe ResolveJá",
                "email": "contato@resolveja.com"
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT"
            }
        },
        "host": "localhost:5000",
        "basePath": "/apidocs",
        "schemes": ["http"],
        "tags": [
            {
                "name": "Autenticação",
                "description": "Operações de login, registro e autenticação"
            },
            {
                "name": "Denúncias",
                "description": "CRUD de denúncias"
            },
            {
                "name": "Administração",
                "description": "Rotas administrativas"
            }
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header usando o esquema Bearer. Exemplo: 'Authorization: Bearer {token}'"
            }
        },
        "definitions": {
            "Denuncia": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "titulo": {"type": "string", "example": "Buraco na rua"},
                    "descricao": {"type": "string", "example": "Há um buraco perigoso na rua X"},
                    "status": {"type": "string", "enum": ["aberta", "em_andamento", "resolvida"], "example": "aberta"},
                    "dataCriacao": {"type": "string", "format": "date-time", "example": "2024-05-19T12:00:00"},
                    "imagemUrl": {"type": "string", "example": "/uploads/denuncia1.jpg"},
                    "latitude": {"type": "number", "example": -23.55052},
                    "longitude": {"type": "number", "example": -46.633308},
                    "usuarioId": {"type": "integer", "example": 2}
                }
            },
            "Usuario": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 2},
                    "nome": {"type": "string", "example": "Maria"},
                    "email": {"type": "string", "example": "maria@email.com"},
                    "role": {"type": "string", "enum": ["admin", "usuario"], "example": "usuario"}
                }
            },
            "Login": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "usuario@email.com"},
                    "senha": {"type": "string", "example": "123456"}
                }
            },
            "Token": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "example": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."}
                }
            }
        }
    })
 
     # Protege as rotas do Swagger
    
 
    return app