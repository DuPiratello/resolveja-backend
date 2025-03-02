import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chave_secreta')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://resolveja_user:senha123@localhost:5432/resolveja')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super_secret_jwt_key')  