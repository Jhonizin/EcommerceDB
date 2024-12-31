from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Definir a chave secreta para sessões
    app.config['SECRET_KEY'] = 'sua-chave-secreta'

    # Caminho do banco de dados
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'db', 'ecommerce.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicialize o db e o login_manager
    db.init_app(app)
    login_manager.init_app(app)

    # Importar e registrar o blueprint
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app

# Definindo o método que carrega o usuário para o Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import Usuario
    return Usuario.query.get(int(user_id))
