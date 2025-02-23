from flask import Flask #type: ignore
from flask_jwt_extended import JWTManager   #type: ignore
from flask_migrate import Migrate   #type: ignore
from flask_socketio import SocketIO #type: ignore
from flask_cors import CORS #type: ignore
from app.models import db

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(app)
    socketio.init_app(app)

    from app.routes import main
    from app.auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')

    return app

