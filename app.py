from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///promoprecio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    ean = db.Column(db.String(13))
    descricao = db.Column(db.String(200), nullable=False)

class Estabelecimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200))

class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimento.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)

@app.route('/')
def home():
    return jsonify({"message": "PromoPreço API v0.1"})

@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'POST':
        data = request.json
        produto = Produto(codigo=data['codigo'], ean=data.get('ean'), descricao=data['descricao'])
        db.session.add(produto)
        db.session.commit()
        return jsonify({"id": produto.id}), 201
    
    produtos = Produto.query.all()
    return jsonify([{"id": p.id, "codigo": p.codigo, "descricao": p.descricao} for p in produtos])

@app.route('/estabelecimentos', methods=['GET', 'POST'])
def estabelecimentos():
    if request.method == 'POST':
        data = request.json
        est = Estabelecimento(nome=data['nome'], url=data.get('url'))
        db.session.add(est)
        db.session.commit()
        return jsonify({"id": est.id}), 201
    
    estabelecimentos = Estabelecimento.query.all()
    return jsonify([{"id": e.id, "nome": e.nome} for e in estabelecimentos])

@app.route('/precos', methods=['GET', 'POST'])
def precos():
    if request.method == 'POST':
        data = request.json
        preco = Preco(produto_id=data['produto_id'], estabelecimento_id=data['estabelecimento_id'], valor=data['valor'])
        db.session.add(preco)
        db.session.commit()
        return jsonify({"id": preco.id}), 201
    
    precos = db.session.query(Preco, Produto, Estabelecimento).join(Produto).join(Estabelecimento).all()
    return jsonify([{"produto": p.descricao, "estabelecimento": e.nome, "valor": pr.valor} for pr, p, e in precos])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))