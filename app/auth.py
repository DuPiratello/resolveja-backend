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

        # ✅ Agora verifica todos os campos obrigatórios
        required_fields = ['username', 'email', 'password', 'phone', 'cpf']
        if not data or any(field not in data for field in required_fields):
            print("❌ Dados incompletos")
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400

        # 🔍 Verificar se email, username ou CPF já existem
        existing_user = User.query.filter(
            (User.email == data['email']) | 
            (User.username == data['username']) |
            (User.cpf == data['cpf'])  # 👈 Novo check para CPF único
        ).first()

        if existing_user:
            conflict_field = 'email' if existing_user.email == data['email'] else 'username' if existing_user.username == data['username'] else 'cpf'
            print(f"❌ {conflict_field.capitalize()} já cadastrado!")
            return jsonify({"error": f"{conflict_field.capitalize()} já está em uso!"}), 409

        # 🔒 Hash da senha
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        # ✅ Cria usuário com todos os campos
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password,
            phone=data['phone'],  # 👈 Novo campo
            cpf=data['cpf']      # 👈 Novo campo
        )
        
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
