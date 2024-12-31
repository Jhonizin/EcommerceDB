from flask_login import login_required, current_user, login_user, logout_user
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app import db
from app.models import Usuario, Anuncio, Pergunta, Compra, Favorito, Categoria, Produto
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

main_bp = Blueprint('main', __name__, template_folder='templates')

# Diretório de upload de imagens
UPLOAD_FOLDER = 'app/static/imagens'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    # Verifica se o usuário está autenticado
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    return redirect(url_for('main.index'))  # Redireciona para a página principal se estiver logado

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):
            login_user(usuario)
            # Após o login bem-sucedido, redireciona para a página inicial
            return redirect(url_for('main.index'))

        flash('Email ou senha inválidos', 'danger')
    
    return render_template('login.html')

@main_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = generate_password_hash(senha)
        usuario = Usuario(nome=nome, email=email, senha=senha_hash)
        db.session.add(usuario)
        db.session.commit()
        flash('Conta criada com sucesso! Você pode fazer login agora.', 'success')
        return redirect(url_for('main.login'))
    return render_template('registrar.html')

@main_bp.route('/index')
@login_required
def index():
    categorias = Categoria.query.all()  # Busca todas as categorias no banco
    return render_template('index.html', usuario=current_user, categorias=categorias)

@main_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/criar-anuncio', methods=['GET', 'POST'])
def criar_anuncio():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        preco = request.form['preco']
        categoria_id = request.form['categoria']  # Pegando o id da categoria escolhida

        # Criar o objeto Anuncio e salvar no banco
        novo_anuncio = Anuncio(
            titulo=titulo,
            descricao=descricao,
            preco=preco,
            categoria_id=categoria_id,  # Associando o anúncio à categoria selecionada
            usuario_id=current_user.id  # Associa o usuário atual ao anúncio
        )

        db.session.add(novo_anuncio)
        db.session.commit()

        flash('Anúncio criado com sucesso!', 'success')
        return redirect(url_for('main.exibir_categoria', id=categoria_id))

    categorias = Categoria.query.all()  # Recupera todas as categorias
    return render_template('criar_anuncio.html', categorias=categorias)

@main_bp.route('/categoria/<int:id>', methods=['GET'])
def exibir_categoria(id):
    categoria = Categoria.query.get(id)
    
    anuncios = Anuncio.query.filter_by(categoria_id=id).all()
    return render_template('categoria.html', categoria=categoria, anuncios=anuncios)


@main_bp.route('/anuncio/<int:id>/perguntar', methods=['POST'])
@login_required
def perguntar(id):
    pergunta = request.form['pergunta']
    anuncio = Anuncio.query.get_or_404(id)
    nova_pergunta = Pergunta(pergunta=pergunta, anuncio_id=anuncio.id, usuario_id=current_user.id)
    db.session.add(nova_pergunta)
    db.session.commit()
    flash('Pergunta enviada com sucesso!', 'success')
    return redirect(url_for('main.visualizar_anuncio', id=anuncio.id))

@main_bp.route('/anuncio/<int:id>/responder/<int:pergunta_id>', methods=['POST'])
@login_required
def responder(id, pergunta_id):
    resposta = request.form['resposta']
    pergunta = Pergunta.query.get_or_404(pergunta_id)
    pergunta.resposta = resposta
    db.session.commit()
    flash('Resposta enviada com sucesso!', 'success')
    return redirect(url_for('main.visualizar_anuncio', id=id))

@main_bp.route('/anuncio/<int:id>', methods=['GET'])
def visualizar_anuncio(id):
    anuncio = Anuncio.query.get_or_404(id)
    return render_template('visualizar_anuncio.html', anuncio=anuncio)

@main_bp.route('/anuncio/<int:id>/comprar', methods=['POST'])
@login_required
def comprar(id):
    anuncio = Anuncio.query.get_or_404(id)
    compra = Compra(anuncio_id=anuncio.id, usuario_id=current_user.id, valor_pago=anuncio.preco)
    db.session.add(compra)
    db.session.commit()
    flash('Compra realizada com sucesso!', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/anuncio/<int:id>/favoritar', methods=['POST'])
@login_required
def favoritar(id):
    anuncio = Anuncio.query.get_or_404(id)
    favorito = Favorito.query.filter_by(anuncio_id=anuncio.id, usuario_id=current_user.id).first()
    if not favorito:
        favorito = Favorito(anuncio_id=anuncio.id, usuario_id=current_user.id)
        db.session.add(favorito)
        db.session.commit()
        flash('Anúncio adicionado aos favoritos!', 'success')
    else:
        flash('Este anúncio já está nos seus favoritos!', 'info')
    return redirect(url_for('main.visualizar_anuncio', id=anuncio.id))

@main_bp.route('/relatorio-compras', methods=['GET'])
@login_required
def relatorio_compras():
    compras = Compra.query.filter_by(usuario_id=current_user.id).all()
    total_compras = sum(compra.valor_pago for compra in compras)
    return render_template('relatorio_compras.html', compras=compras, total_compras=total_compras)

@main_bp.route('/relatorio-vendas', methods=['GET'])
@login_required
def relatorio_vendas():
    anuncios = Anuncio.query.filter_by(usuario_id=current_user.id).all()
    vendas = []
    for anuncio in anuncios:
        vendas.append({
            'anuncio': anuncio.titulo,
            'quantidade': len(anuncio.vendas),
            'total': sum(compra.valor_pago for compra in anuncio.vendas)
        })
    return render_template('relatorio_vendas.html', vendas=vendas)

@main_bp.route('/meus-anuncios', methods=['GET', 'POST'])
@login_required
def meus_anuncios():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])

        novo_anuncio = Anuncio(
            titulo=titulo,
            descricao=descricao,
            preco=preco,
            usuario_id=current_user.id
        )
        db.session.add(novo_anuncio)
        db.session.commit()
        flash("Anúncio adicionado com sucesso!", "success")
        return redirect(url_for('main.meus_anuncios'))

    anuncios = Anuncio.query.filter_by(usuario_id=current_user.id).all()
    categorias = Categoria.query.all()
    return render_template('meus_anuncios.html', anuncios=anuncios, categorias=categorias)
