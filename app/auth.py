from flask import Blueprint, request, jsonify   #type:ignore
from app.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  #type:ignore

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Dados incompletos"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email já cadastrado"}), 409

    # Se não for passado role, define "user" por padrão
    role = data.get('role', 'user')
    if role not in ["user", "admin"]:
        return jsonify({"error": "Role inválida"}), 400

    new_user = User(username=data['username'], email=data['email'], role=role)
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuário registrado com sucesso!", "role": new_user.role}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Dados incompletos"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Credenciais inválidas"}), 401

    access_token = create_access_token(identity=str(user.id))  # Apenas o ID como string
    return jsonify({"access_token": access_token}), 200

@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()  # Agora current_user é apenas uma string (o ID do usuário)
    return jsonify({
        "message": "Você acessou uma rota protegida!",
        "user_id": current_user  # Apenas retorna a string diretamente
    }), 200
