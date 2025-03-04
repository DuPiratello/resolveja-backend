from flask import Flask  # type: ignore
from flask_jwt_extended import JWTManager  # type: ignore
from flask_migrate import Migrate  # type: ignore
from flask_socketio import SocketIO  # type: ignore
from flask_cors import CORS  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from config import Config  # Importado antes!

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
    CORS(app)
    socketio.init_app(app)

    # ⚠️ Importações de rotas depois da inicialização do db
    from app.routes import main, admin_routes
    from app.auth import auth
    from app.routes import denuncia_routes  # 📌 Importa as rotas de denúncias

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin_routes, url_prefix='/admin')  # Rotas admin
    app.register_blueprint(denuncia_routes, url_prefix='/api')  # 📌 Adiciona as rotas de denúncias

    return app