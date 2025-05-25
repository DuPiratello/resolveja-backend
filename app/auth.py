from flask import Blueprint, request, jsonify   #type:ignore
from app.models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity  #type:ignore
from werkzeug.security import generate_password_hash #type:ignore

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    Registra um novo usuário
    ---
    tags:
      - Autenticação
    summary: Registro de usuário
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
            - phone
            - cpf
          properties:
            username:
              type: string
              example: maria
            email:
              type: string
              example: maria@email.com
            password:
              type: string
              example: 123456
            phone:
              type: string
              example: "11999999999"
            cpf:
              type: string
              example: "12345678900"
    responses:
      201:
        description: Usuário registrado com sucesso
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Dados incompletos
      409:
        description: Email, username ou CPF já está em uso
      500:
        description: Erro interno no servidor
    """
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
            phone=data['phone'],  
            cpf=data['cpf']      
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
    """
    Realiza login do usuário
    ---
    tags:
      - Autenticação
    summary: Login de usuário
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: maria@email.com
            password:
              type: string
              example: 123456
    responses:
      200:
        description: Login realizado com sucesso
        schema:
          type: object
          properties:
            access_token:
              type: string
      400:
        description: Dados incompletos
      401:
        description: Credenciais inválidas
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Dados incompletos"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Credenciais inválidas"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role})
    return jsonify({"access_token": access_token}), 200

@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """
    Rota protegida (exemplo)
    ---
    tags:
      - Autenticação
    summary: Testa acesso autenticado
    security:
      - Bearer: []
    responses:
      200:
        description: Acesso autorizado
        schema:
          type: object
          properties:
            message:
              type: string
            user_id:
              type: string
      401:
        description: Não autorizado
    """
    current_user = get_jwt_identity()  # Agora current_user é apenas uma string (o ID do usuário)
    return jsonify({
        "message": "Você acessou uma rota protegida!",
        "user_id": current_user  # Apenas retorna a string diretamente
    }), 200
