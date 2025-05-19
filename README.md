# Backend - ResolveJá

Este diretório contém a API backend do projeto **ResolveJá**, responsável por gerenciar autenticação, denúncias, usuários e integrações com o frontend Angular.

---

## 📦 Estrutura de Pastas

```
backend/
├── app/
│   ├── __init__.py           # Inicialização da aplicação Flask e registro dos blueprints
│   ├── auth.py               # Rotas e lógica de autenticação (login, registro, JWT)
│   ├── decorators.py         # Decorators customizados para controle de acesso (ex: role_required)
│   ├── denuncias.py          # Rotas e lógica de CRUD de denúncias
│   ├── models.py             # Definição dos modelos SQLAlchemy (Usuário, Denúncia, etc.)
│   ├── routes.py             # Rotas principais e administrativas
│   └── __pycache__/
├── config.py                 # Configurações da aplicação (variáveis de ambiente, banco, JWT)
├── requirements.txt          # Dependências Python do projeto
├── run.py                    # Script principal para rodar o servidor Flask
├── frontend/                 # Frontend Angular (ver README próprio)
├── migrations/               # Migrações Alembic para o banco de dados
└── ...
```

---

## 🚀 Tecnologias e Implementações Padrão Utilizadas

- **Flask**  
  Framework web principal, utilizado para criar rotas HTTP, middlewares e inicialização da aplicação.

- **Flask Blueprints**  
  Modularização das rotas em blueprints:
  - `main` (página inicial)
  - `auth` (autenticação)
  - `admin_routes` (rotas administrativas)
  - `denuncia_routes` (rotas de denúncias)

- **Flask-JWT-Extended**  
  Autenticação baseada em JWT para proteger rotas e identificar usuários. Tokens são armazenados no frontend e enviados no header Authorization.

- **Flask-Migrate + Alembic**  
  Gerenciamento de migrações do banco de dados via comandos Alembic, facilitando a evolução do schema.

- **Flask-CORS**  
  Permite requisições cross-origin do frontend Angular, garantindo integração segura.

- **Flask-SocketIO**  
  Suporte a WebSockets para funcionalidades em tempo real (ex: notificações de novas denúncias).

- **SQLAlchemy**  
  ORM para definição dos modelos e manipulação do banco de dados relacional. Relacionamentos entre usuários e denúncias são definidos via ForeignKey.

- **Padrão MVC (Model-View-Controller)**  
  Separação entre modelos (`models.py`), rotas/controllers (`routes.py`, `denuncias.py`, etc.) e lógica de autenticação (`auth.py`).

- **Decorators personalizados**  
  Exemplo: `role_required` para controle de acesso por perfil, `jwt_required` para proteger rotas.

- **Configuração via arquivo `config.py`**  
  Centralização das configurações sensíveis e variáveis de ambiente, como URI do banco, secret keys, configurações de JWT e CORS.

- **Validação e tratamento de erros**  
  As rotas validam dados de entrada e retornam mensagens de erro padronizadas em caso de falha de autenticação, autorização ou dados inválidos.

- **Upload de arquivos**  
  Suporte a upload de imagens nas denúncias, com armazenamento local ou em serviço externo (dependendo da configuração).

---

## ❌ Implementações Padrão NÃO Utilizadas

- **Django**  
  Não foi utilizado o framework Django nem seu ORM, admin ou sistema de rotas.

- **OAuth2 / Social Auth**  
  Não há autenticação via provedores externos (Google, Facebook, etc.).

- **Swagger/OpenAPI**  
  Não há documentação automática de API via Swagger.

- **GraphQL**  
  Não há endpoints GraphQL, apenas REST.

---

## 🛣️ Rotas e Blueprints

- `/api/denuncias`
  - `GET`: Lista todas as denúncias públicas, com filtros opcionais por status, tipo, data, etc.
  - `POST`: Cria uma nova denúncia (JWT obrigatório, validação de campos e upload de imagem)
  - `GET /api/denuncias/<id>`: Detalhes de uma denúncia específica
  - `PUT /api/denuncias/<id>`: Atualiza denúncia (restrito ao autor/admin)
  - `DELETE /api/denuncias/<id>`: Remove denúncia (restrito ao autor/admin)

- `/api/minhas-denuncias`
  - `GET`: Lista denúncias do usuário autenticado

- `/auth/`
  - `POST /auth/login`: Login de usuário, retorna JWT
  - `POST /auth/register`: Cadastro de novo usuário
  - `POST /auth/refresh`: Gera novo token JWT

- `/admin/`
  - Rotas administrativas (restritas por decorator, ex: listar todos os usuários, alterar status de denúncia)

- `/`
  - Página inicial (healthcheck ou mensagem de boas-vindas)

---

## 🗄️ Banco de Dados

- Modelos definidos em [`app/models.py`](backend/app/models.py):
  - **Usuário:** id, nome, email, senha (hash), role (admin/usuário), data de criação
  - **Denúncia:** id, título, descrição, status, data de criação, imagem, latitude, longitude, usuário_id (relacionamento)
- Migrações gerenciadas via Alembic em [`migrations/`](backend/migrations/)
- Uso de SQLAlchemy para queries, inserções, atualizações e relacionamentos

---

## 🔒 Autenticação e Autorização

- JWT obrigatório para rotas protegidas
- Decorators para exigir autenticação e/ou perfil de usuário (`role_required`)
- Tokens gerados e validados via Flask-JWT-Extended
- Senhas armazenadas com hash seguro (ex: bcrypt)

---

## 📤 Upload de Imagens

- Rotas de denúncia aceitam upload de imagem via multipart/form-data
- Imagens são salvas em diretório específico ou serviço externo, e o caminho é armazenado no banco
- Validação de tipo e tamanho de arquivo

---

## 🛠️ Como rodar o backend

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure variáveis de ambiente em `config.py` (ex: URI do banco, secret keys, diretório de uploads)
3. Execute as migrações:
   ```bash
   flask db upgrade
   ```
4. Rode o servidor:
   ```bash
   flask run
   ```
   ou
   ```bash
   python run.py
   ```

---

## 🧪 Testes

- Não há framework de testes automatizados configurado por padrão (ex: pytest, unittest).
- Testes podem ser feitos via ferramentas como Postman, Insomnia ou scripts manuais.
- Recomenda-se criar testes para autenticação, criação de denúncia, upload de imagem e permissões de acesso.

---

## 📄 Observações

- O backend está preparado para integração com o frontend Angular localizado em [`backend/frontend/`](backend/frontend/).
- O CORS está habilitado para permitir requisições do frontend.
- Para detalhes do frontend, consulte o README correspondente.

---

## 📚 Referências

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)