from app import create_app, db
from flask_login import LoginManager
from app.models import Usuario, Anuncio, Categoria

# Criar a aplicação Flask
app = create_app()

# Inicializar o LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Função para criar categorias
def criar_categorias():
    # Criando categorias com IDs 1, 2 e 3
    if not Categoria.query.get(1):
        categoria1 = Categoria(id=1, nome='Categoria 1')
        db.session.add(categoria1)
    if not Categoria.query.get(2):
        categoria2 = Categoria(id=2, nome='Categoria 2')
        db.session.add(categoria2)
    if not Categoria.query.get(3):
        categoria3 = Categoria(id=3, nome='Categoria 3')
        db.session.add(categoria3)

    db.session.commit()
    print('Categorias adicionadas com sucesso!')

with app.app_context():
    if  not Categoria.query.first():
        db.session.add_all([
            Categoria(id=1, nome="Eletrônicos"),
            Categoria(id=2, nome="Móveis"),
            Categoria(id=3, nome="Roupas")
        ])
        db.session.commit()

# Rodar o servidor Flask
if __name__ == "__main__":
    # Criar as tabelas no banco de dados (executado uma vez)
    with app.app_context():  # Garantir que estamos dentro do contexto da aplicação
        db.create_all()  # Criar as tabelas se ainda não existirem

        # Chamar a função para criar as categorias
        criar_categorias()

        # Exemplo de adicionar um novo anúncio
        novo_anuncio = Anuncio(
            titulo='Novo Anuncio',
            descricao='Descrição do novo anúncio',
            preco=100.0,
            categoria_id=1,
            usuario_id=1
        )
        db.session.add(novo_anuncio)
        db.session.commit()

    # Rodar o servidor Flask após a criação do anúncio
    app.run(debug=True)
