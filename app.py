from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///promoprecco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    ean = db.Column(db.String(13))

class Estabelecimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(14))

class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimento.id'), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    data_coleta = db.Column(db.DateTime, default=datetime.utcnow)

# Rotas
@app.route('/')
def home():
    return render_template('cadastros.html')

@app.route('/api')
def api_status():
    return jsonify({'app': 'PromoPreço', 'status': 'running'})

# Produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    produtos = Produto.query.all()
    return jsonify([{'id': p.id, 'codigo': p.codigo, 'descricao': p.descricao, 'ean': p.ean} for p in produtos])

@app.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.json
    produto = Produto(codigo=data['codigo'], descricao=data['descricao'], ean=data.get('ean'))
    db.session.add(produto)
    db.session.commit()
    return jsonify({'id': produto.id}), 201

# Estabelecimentos
@app.route('/estabelecimentos', methods=['GET'])
def listar_estabelecimentos():
    estabelecimentos = Estabelecimento.query.all()
    return jsonify([{'id': e.id, 'nome': e.nome, 'cnpj': e.cnpj} for e in estabelecimentos])

@app.route('/estabelecimentos', methods=['POST'])
def criar_estabelecimento():
    data = request.json
    estabelecimento = Estabelecimento(nome=data['nome'], cnpj=data.get('cnpj'))
    db.session.add(estabelecimento)
    db.session.commit()
    return jsonify({'id': estabelecimento.id}), 201

# Preços
@app.route('/precos', methods=['GET'])
def listar_precos():
    precos = Preco.query.all()
    return jsonify([{
        'id': p.id,
        'produto_id': p.produto_id,
        'estabelecimento_id': p.estabelecimento_id,
        'preco': float(p.preco),
        'data_coleta': p.data_coleta.isoformat()
    } for p in precos])

@app.route('/precos', methods=['POST'])
def criar_preco():
    data = request.json
    preco = Preco(
        produto_id=data['produto_id'],
        estabelecimento_id=data['estabelecimento_id'],
        preco=data['preco']
    )
    db.session.add(preco)
    db.session.commit()
    return jsonify({'id': preco.id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)