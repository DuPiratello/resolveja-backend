from flask import Blueprint, request, jsonify   #type:ignore
from app.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  #type:ignore
from werkzeug.security import generate_password_hash #type:ignore

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("📌 Dados Recebidos:", data)

        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            print("❌ Dados incompletos")
            return jsonify({"error": "Dados incompletos"}), 400

        # 🔍 Verificar se o e-mail ou username já estão cadastrados
        existing_user = User.query.filter(
            (User.email == data['email']) | (User.username == data['username'])
        ).first()

        if existing_user:
            print(f"❌ Usuário já cadastrado! username: {existing_user.username}, email: {existing_user.email}")
            return jsonify({"error": "Usuário ou e-mail já cadastrado!"}), 409  # 🔥 409 = Conflict

        # 🔒 Hash da senha antes de salvar
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # ✅ Criar novo usuário
        new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        print("✅ Usuário registrado com sucesso!")
        return jsonify({"message": "Usuário registrado com sucesso!"}), 201

    except Exception as e:
        print("❌ ERRO AO REGISTRAR:", str(e))
        return jsonify({"error": "Erro interno no servidor"}), 500


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
