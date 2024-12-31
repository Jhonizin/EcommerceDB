from flask_sqlalchemy import SQLAlchemy
from app import db
from flask_login import UserMixin

class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)

    # Define a relationship from Categoria to Anuncio
    anuncios = db.relationship('Anuncio', back_populates='categoria')

class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    anuncio = db.relationship('Anuncio', backref='favoritos', lazy=True)

    def __repr__(self):
        return f"<Favorito {self.id}>"

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)
    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    valor_pago = db.Column(db.Float, nullable=False)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

    anuncios = db.relationship('Anuncio', back_populates='usuario', lazy=True)
    compras = db.relationship('Compra', backref='usuario', lazy=True)
    favoritos = db.relationship('Favorito', backref='usuario_favorito', lazy=True)
    produtos = db.relationship('Produto', back_populates='usuario', lazy=True)

    def __repr__(self):
        return f"<Usuario {self.nome}>"

class Imagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))
    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), nullable=False)

    anuncio = db.relationship('Anuncio', backref=db.backref('imagens', lazy=True))

class Produto(db.Model):
    __tablename__ = 'produto'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    condicao = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    usuario = db.relationship('Usuario', back_populates='produtos', lazy=True)

    def __repr__(self):
        return f"<Produto {self.titulo}>"

class Anuncio(db.Model):
    __tablename__ = 'anuncio'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    categoria = db.relationship('Categoria', back_populates='anuncios', lazy=True)
    usuario = db.relationship('Usuario', back_populates='anuncios', lazy=True)

    def __repr__(self):
        return f"<Anuncio {self.titulo}>"

class Pergunta(db.Model):
    __tablename__ = 'pergunta'
    
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    anuncio_id = db.Column(db.Integer, db.ForeignKey('anuncio.id'), nullable=False)

    usuario = db.relationship('Usuario', backref='perguntas_usuario', lazy=True)
    anuncio = db.relationship('Anuncio', backref='perguntas_anuncio', lazy=True)

    def __repr__(self):
        return f"<Pergunta {self.texto}>"

# Criando um novo anúncio
novo_anuncio = Anuncio(
    titulo="Novo Anúncio",
    descricao="Descrição do anúncio",
    preco=100.0,
    usuario_id=1,  # O ID do usuário logado ou de outro usuário
    categoria_id=1  # O ID de uma categoria válida
)
