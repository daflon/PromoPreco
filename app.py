from flask import Flask, request, jsonify, render_template, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from rapidfuzz import fuzz, process
import re
import time
import logging
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import xlsxwriter
from sqlalchemy import func, desc, asc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///promoprecco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

db = SQLAlchemy(app)
cache = Cache(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos
class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    ean = db.Column(db.String(13))

class Estabelecimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(14))
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)

class Preco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('estabelecimento.id'), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    data_coleta = db.Column(db.DateTime, default=datetime.utcnow)

# Funções de validação
def validar_cnpj(cnpj):
    if not cnpj:
        return True  # CNPJ é opcional
    cnpj = re.sub(r'\D', '', cnpj)
    return len(cnpj) == 14 and cnpj.isdigit()

def validar_ean(ean):
    if not ean:
        return True  # EAN é opcional
    ean = re.sub(r'\D', '', ean)
    return len(ean) == 13 and ean.isdigit()

def sanitizar_busca(termo):
    """Sanitiza termo de busca removendo caracteres perigosos"""
    if not termo:
        return ''
    # Remove caracteres especiais, mantém apenas alfanuméricos, espaços e acentos
    termo_limpo = re.sub(r'[^\w\s\u00C0-\u017F]', '', termo)
    return termo_limpo.strip()[:100]  # Limita a 100 caracteres

def busca_fuzzy(termo, opcoes, limite=5):
    """Realiza busca fuzzy em uma lista de opções"""
    if not termo or not opcoes:
        return []
    
    # Busca fuzzy com score mínimo de 60
    matches = process.extract(termo, opcoes, limit=limite, scorer=fuzz.partial_ratio)
    return [match[0] for match in matches if match[1] >= 60]



# Rotas
@app.route('/')
def home():
    return render_template('dashboard_adminlte.html')

@app.route('/cadastros')
def cadastros():
    return render_template('cadastros.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/adminlte')
def dashboard_adminlte():
    return render_template('dashboard_adminlte.html')

@app.route('/dashboard/stats', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60)
def dashboard_stats():
    """Retorna estatísticas para o dashboard"""
    try:
        total_produtos = Produto.query.count()
        total_estabelecimentos = Estabelecimento.query.count()
        total_precos = Preco.query.count()
        
        return jsonify({
            'total_produtos': total_produtos,
            'total_estabelecimentos': total_estabelecimentos,
            'total_precos': total_precos
        })
    except Exception as e:
        logger.error(f"Erro ao carregar estatísticas: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/comparar/<int:produto_id>')
@limiter.limit("30 per minute")
@cache.cached(timeout=60)
def comparar_precos(produto_id):
    """Compara preços de um produto específico"""
    try:
        produto = Produto.query.get_or_404(produto_id)
        
        precos = db.session.query(Preco, Estabelecimento).join(
            Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
        ).filter(Preco.produto_id == produto_id).all()
        
        resultado = {
            'produto': {
                'id': produto.id,
                'descricao': produto.descricao,
                'ean': produto.ean
            },
            'precos': []
        }
        
        for preco, estabelecimento in precos:
            resultado['precos'].append({
                'preco': float(preco.preco),
                'data_coleta': preco.data_coleta.isoformat(),
                'estabelecimento': {
                    'id': estabelecimento.id,
                    'nome': estabelecimento.nome,
                    'bairro': estabelecimento.bairro,
                    'cidade': estabelecimento.cidade
                }
            })
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao comparar preços: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api')
def api_status():
    return jsonify({'app': 'PromoPreço', 'status': 'running'})

# Produtos
@app.route('/produtos', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60, query_string=True)
def listar_produtos():
    start_time = time.perf_counter()
    
    try:
        busca = sanitizar_busca(request.args.get('q', ''))
        
        if busca:
            produtos = Produto.query.filter(
                db.or_(
                    Produto.descricao.ilike(f'%{busca}%'),
                    Produto.ean.ilike(f'%{busca}%')
                )
            ).all()
            
            if len(produtos) < 3:
                todos_produtos = Produto.query.all()
                descricoes = [p.descricao for p in todos_produtos]
                matches_fuzzy = busca_fuzzy(busca, descricoes)
                
                if matches_fuzzy:
                    produtos_fuzzy = Produto.query.filter(
                        Produto.descricao.in_(matches_fuzzy)
                    ).all()
                    produtos_ids = {p.id for p in produtos}
                    for p in produtos_fuzzy:
                        if p.id not in produtos_ids:
                            produtos.append(p)
        else:
            produtos = Produto.query.all()
        
        resultado = [{
            'id': p.id, 
            'descricao': p.descricao, 
            'ean': p.ean
        } for p in produtos]
        
        tempo_execucao = time.perf_counter() - start_time
        if tempo_execucao > 0.5:
            logger.warning(f"Query lenta em produtos: {tempo_execucao:.3f}s para '{busca}'")
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro na busca de produtos: {str(e)}")
        return jsonify({'error': 'Erro interno na busca'}), 500

@app.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.json
    
    if not data.get('descricao'):
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    
    if not validar_ean(data.get('ean')):
        return jsonify({'error': 'EAN deve ter 13 dígitos'}), 400
    
    produto = Produto(
        descricao=data['descricao'], 
        ean=data.get('ean')
    )
    db.session.add(produto)
    db.session.commit()
    return jsonify({'id': produto.id}), 201

@app.route('/produtos/<int:id>', methods=['PUT'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    data = request.json
    
    if not data.get('descricao'):
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    
    if not validar_ean(data.get('ean')):
        return jsonify({'error': 'EAN deve ter 13 dígitos'}), 400
    
    produto.descricao = data['descricao']
    produto.ean = data.get('ean')
    db.session.commit()
    return jsonify({'success': True})

@app.route('/produtos/<int:id>', methods=['DELETE'])
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/produtos/com-precos', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60, query_string=True)
def produtos_com_precos():
    """Lista apenas produtos que têm preços cadastrados"""
    try:
        produtos_com_preco = db.session.query(Produto).join(Preco).distinct().all()
        resultado = [{
            'id': p.id,
            'descricao': p.descricao,
            'ean': p.ean
        } for p in produtos_com_preco]
        return jsonify(resultado)
    except Exception as e:
        logger.error(f"Erro ao buscar produtos com preços: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

# Estabelecimentos
@app.route('/estabelecimentos', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60, query_string=True)
def listar_estabelecimentos():
    start_time = time.perf_counter()
    
    try:
        busca = sanitizar_busca(request.args.get('q', ''))
        
        if busca:
            estabelecimentos = Estabelecimento.query.filter(
                db.or_(
                    Estabelecimento.nome.ilike(f'%{busca}%'),
                    Estabelecimento.bairro.ilike(f'%{busca}%'),
                    Estabelecimento.cidade.ilike(f'%{busca}%'),
                    Estabelecimento.cnpj.ilike(f'%{busca}%')
                )
            ).all()
            
            # Busca fuzzy se poucos resultados
            if len(estabelecimentos) < 3:
                todos_estabelecimentos = Estabelecimento.query.all()
                nomes = [e.nome for e in todos_estabelecimentos]
                matches_fuzzy = busca_fuzzy(busca, nomes)
                
                if matches_fuzzy:
                    estabelecimentos_fuzzy = Estabelecimento.query.filter(
                        Estabelecimento.nome.in_(matches_fuzzy)
                    ).all()
                    estabelecimentos_ids = {e.id for e in estabelecimentos}
                    for e in estabelecimentos_fuzzy:
                        if e.id not in estabelecimentos_ids:
                            estabelecimentos.append(e)
        else:
            estabelecimentos = Estabelecimento.query.all()
        
        resultado = [{
            'id': e.id, 
            'nome': e.nome, 
            'cnpj': e.cnpj,
            'bairro': e.bairro,
            'cidade': e.cidade
        } for e in estabelecimentos]
        
        tempo_execucao = time.perf_counter() - start_time
        if tempo_execucao > 0.5:
            logger.warning(f"Query lenta em estabelecimentos: {tempo_execucao:.3f}s para '{busca}'")
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro na busca de estabelecimentos: {str(e)}")
        return jsonify({'error': 'Erro interno na busca'}), 500

@app.route('/estabelecimentos', methods=['POST'])
def criar_estabelecimento():
    data = request.json
    
    if not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    if not data.get('bairro'):
        return jsonify({'error': 'Bairro é obrigatório'}), 400
        
    if not data.get('cidade'):
        return jsonify({'error': 'Cidade é obrigatória'}), 400
    
    if not validar_cnpj(data.get('cnpj')):
        return jsonify({'error': 'CNPJ deve ter 14 dígitos'}), 400
    
    estabelecimento = Estabelecimento(
        nome=data['nome'], 
        cnpj=data.get('cnpj'),
        bairro=data['bairro'],
        cidade=data['cidade']
    )
    db.session.add(estabelecimento)
    db.session.commit()
    return jsonify({'id': estabelecimento.id}), 201

@app.route('/estabelecimentos/<int:id>', methods=['PUT'])
def editar_estabelecimento(id):
    estabelecimento = Estabelecimento.query.get_or_404(id)
    data = request.json
    
    if not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    if not data.get('bairro'):
        return jsonify({'error': 'Bairro é obrigatório'}), 400
        
    if not data.get('cidade'):
        return jsonify({'error': 'Cidade é obrigatória'}), 400
    
    if not validar_cnpj(data.get('cnpj')):
        return jsonify({'error': 'CNPJ deve ter 14 dígitos'}), 400
    
    estabelecimento.nome = data['nome']
    estabelecimento.cnpj = data.get('cnpj')
    estabelecimento.bairro = data['bairro']
    estabelecimento.cidade = data['cidade']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/estabelecimentos/<int:id>', methods=['DELETE'])
def excluir_estabelecimento(id):
    estabelecimento = Estabelecimento.query.get_or_404(id)
    db.session.delete(estabelecimento)
    db.session.commit()
    return jsonify({'success': True})

# Preços
@app.route('/precos', methods=['GET'])
def listar_precos():
    # Busca avançada com filtros
    produto_id = request.args.get('produto_id')
    estabelecimento_id = request.args.get('estabelecimento_id')
    preco_min = request.args.get('preco_min')
    preco_max = request.args.get('preco_max')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    query = Preco.query
    
    if produto_id:
        query = query.filter(Preco.produto_id == produto_id)
    if estabelecimento_id:
        query = query.filter(Preco.estabelecimento_id == estabelecimento_id)
    if preco_min:
        query = query.filter(Preco.preco >= float(preco_min))
    if preco_max:
        query = query.filter(Preco.preco <= float(preco_max))
    
    precos = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'precos': [{
            'id': p.id,
            'produto_id': p.produto_id,
            'estabelecimento_id': p.estabelecimento_id,
            'preco': float(p.preco),
            'data_coleta': p.data_coleta.isoformat()
        } for p in precos.items],
        'total': precos.total,
        'pages': precos.pages,
        'current_page': page
    })

@app.route('/precos', methods=['POST'])
def criar_preco():
    data = request.json
    
    if not data.get('produto_id') or not data.get('estabelecimento_id') or not data.get('preco'):
        return jsonify({'error': 'Produto, estabelecimento e preço são obrigatórios'}), 400
    
    try:
        preco_valor = float(data['preco'])
        if preco_valor <= 0:
            return jsonify({'error': 'Preço deve ser maior que zero'}), 400
    except ValueError:
        return jsonify({'error': 'Preço deve ser um número válido'}), 400
    
    preco = Preco(
        produto_id=data['produto_id'],
        estabelecimento_id=data['estabelecimento_id'],
        preco=preco_valor
    )
    db.session.add(preco)
    db.session.commit()
    return jsonify({'id': preco.id}), 201

@app.route('/precos/<int:id>', methods=['PUT'])
def editar_preco(id):
    preco = Preco.query.get_or_404(id)
    data = request.json
    
    if not data.get('produto_id') or not data.get('estabelecimento_id') or not data.get('preco'):
        return jsonify({'error': 'Produto, estabelecimento e preço são obrigatórios'}), 400
    
    try:
        preco_valor = float(data['preco'])
        if preco_valor <= 0:
            return jsonify({'error': 'Preço deve ser maior que zero'}), 400
    except ValueError:
        return jsonify({'error': 'Preço deve ser um número válido'}), 400
    
    preco.produto_id = data['produto_id']
    preco.estabelecimento_id = data['estabelecimento_id']
    preco.preco = preco_valor
    db.session.commit()
    return jsonify({'success': True})

@app.route('/precos/<int:id>', methods=['DELETE'])
def excluir_preco(id):
    preco = Preco.query.get_or_404(id)
    db.session.delete(preco)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/precos/detalhados', methods=['GET'])
@limiter.limit("20 per minute")
@cache.cached(timeout=30, query_string=True)
def listar_precos_detalhados():
    """Lista preços com informações detalhadas de produto e estabelecimento"""
    try:
        busca = sanitizar_busca(request.args.get('q', ''))
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        query = db.session.query(Preco, Produto, Estabelecimento).join(
            Produto, Preco.produto_id == Produto.id
        ).join(
            Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
        )
        
        if busca:
            query = query.filter(
                db.or_(
                    Produto.descricao.ilike(f'%{busca}%'),
                    Estabelecimento.nome.ilike(f'%{busca}%'),
                    Estabelecimento.bairro.ilike(f'%{busca}%')
                )
            )
        
        query = query.order_by(Preco.data_coleta.desc())
        precos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)
        
        resultado = []
        for preco, produto, estabelecimento in precos_paginados.items:
            resultado.append({
                'id': preco.id,
                'produto_id': preco.produto_id,
                'estabelecimento_id': preco.estabelecimento_id,
                'preco': float(preco.preco),
                'data_coleta': preco.data_coleta.isoformat(),
                'produto': {
                    'id': produto.id,
                    'nome': produto.descricao
                },
                'estabelecimento': {
                    'id': estabelecimento.id,
                    'nome': estabelecimento.nome,
                    'bairro': estabelecimento.bairro,
                    'cidade': estabelecimento.cidade
                }
            })
        
        return jsonify({
            'precos': resultado,
            'total': precos_paginados.total,
            'pages': precos_paginados.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Erro na busca de preços detalhados: {str(e)}")
        return jsonify({'error': 'Erro interno na busca'}), 500





@app.route('/comparar', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60, query_string=True)
def comparar_com_busca():
    """Comparação com busca fuzzy"""
    try:
        termo = sanitizar_busca(request.args.get('q', ''))
        if not termo:
            return jsonify({'error': 'Termo de busca obrigatório'}), 400
        
        produtos = Produto.query.filter(
            Produto.descricao.ilike(f'%{termo}%')
        ).all()
        
        if len(produtos) < 3:
            todos_produtos = Produto.query.all()
            descricoes = [p.descricao for p in todos_produtos]
            matches_fuzzy = busca_fuzzy(termo, descricoes)
            
            if matches_fuzzy:
                produtos_fuzzy = Produto.query.filter(
                    Produto.descricao.in_(matches_fuzzy)
                ).all()
                produtos_ids = {p.id for p in produtos}
                for p in produtos_fuzzy:
                    if p.id not in produtos_ids:
                        produtos.append(p)
        
        resultado = []
        for produto in produtos:
            precos = db.session.query(Preco, Estabelecimento).join(
                Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
            ).filter(Preco.produto_id == produto.id).order_by(Preco.preco).all()
            
            if precos:
                produto_data = {
                    'produto': {
                        'id': produto.id,
                        'descricao': produto.descricao,
                        'ean': produto.ean
                    },
                    'precos': []
                }
                
                for preco, estabelecimento in precos:
                    produto_data['precos'].append({
                        'preco': float(preco.preco),
                        'data_coleta': preco.data_coleta.isoformat(),
                        'estabelecimento': {
                            'id': estabelecimento.id,
                            'nome': estabelecimento.nome,
                            'bairro': estabelecimento.bairro,
                            'cidade': estabelecimento.cidade
                        }
                    })
                
                resultado.append(produto_data)
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro na comparação com busca: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

# Relatórios e Exportação
@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html')

@app.route('/api/historico-precos/<int:produto_id>')
@limiter.limit("20 per minute")
@cache.cached(timeout=300, query_string=True)
def historico_precos(produto_id):
    """Histórico de preços de um produto"""
    try:
        produto = Produto.query.get_or_404(produto_id)
        dias = int(request.args.get('dias', 30))
        data_limite = datetime.utcnow() - timedelta(days=dias)
        
        historico = db.session.query(
            Preco, Estabelecimento
        ).join(
            Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
        ).filter(
            Preco.produto_id == produto_id,
            Preco.data_coleta >= data_limite
        ).order_by(Preco.data_coleta.desc()).all()
        
        resultado = {
            'produto': {
                'id': produto.id,
                'descricao': produto.descricao,
                'ean': produto.ean
            },
            'historico': []
        }
        
        for preco, estabelecimento in historico:
            resultado['historico'].append({
                'preco': float(preco.preco),
                'data_coleta': preco.data_coleta.isoformat(),
                'estabelecimento': {
                    'id': estabelecimento.id,
                    'nome': estabelecimento.nome,
                    'bairro': estabelecimento.bairro,
                    'cidade': estabelecimento.cidade
                }
            })
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro no histórico de preços: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/relatorio-precos')
@limiter.limit("10 per minute")
def relatorio_precos():
    """Relatório geral de preços com filtros"""
    try:
        formato = request.args.get('formato', 'json')
        dias = int(request.args.get('dias', 7))
        produto_id = request.args.get('produto_id')
        estabelecimento_id = request.args.get('estabelecimento_id')
        
        data_limite = datetime.utcnow() - timedelta(days=dias)
        
        query = db.session.query(
            Preco, Produto, Estabelecimento
        ).join(
            Produto, Preco.produto_id == Produto.id
        ).join(
            Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
        ).filter(
            Preco.data_coleta >= data_limite
        )
        
        if produto_id:
            query = query.filter(Preco.produto_id == produto_id)
        if estabelecimento_id:
            query = query.filter(Preco.estabelecimento_id == estabelecimento_id)
        
        precos = query.order_by(Preco.data_coleta.desc()).all()
        
        dados = []
        for preco, produto, estabelecimento in precos:
            dados.append({
                'produto': produto.descricao,
                'ean': produto.ean or '',
                'estabelecimento': estabelecimento.nome,
                'bairro': estabelecimento.bairro,
                'cidade': estabelecimento.cidade,
                'preco': float(preco.preco),
                'data_coleta': preco.data_coleta.strftime('%d/%m/%Y %H:%M')
            })
        
        if formato == 'csv':
            return exportar_csv(dados, 'relatorio_precos.csv')
        elif formato == 'excel':
            return exportar_excel(dados, 'relatorio_precos.xlsx')
        elif formato == 'pdf':
            return exportar_pdf(dados, 'Relatório de Preços')
        else:
            return jsonify(dados)
            
    except Exception as e:
        logger.error(f"Erro no relatório de preços: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

def exportar_csv(dados, filename):
    """Exporta dados para CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=dados[0].keys() if dados else [])
    writer.writeheader()
    writer.writerows(dados)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def exportar_excel(dados, filename):
    """Exporta dados para Excel"""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    if dados:
        headers = list(dados[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        for row, item in enumerate(dados, 1):
            for col, header in enumerate(headers):
                worksheet.write(row, col, item[header])
    
    workbook.close()
    output.seek(0)
    
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def exportar_pdf(dados, titulo):
    """Exporta dados para PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph(titulo, styles['Title'])
    elements.append(title)
    
    if dados:
        headers = list(dados[0].keys())
        table_data = [headers]
        
        for item in dados:
            row = [str(item[header]) for header in headers]
            table_data.append(row)
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio.pdf'
    return response

# Ordenação avançada para listagens
@app.route('/precos/ordenados', methods=['GET'])
@limiter.limit("30 per minute")
@cache.cached(timeout=60, query_string=True)
def listar_precos_ordenados():
    """Lista preços com ordenação avançada"""
    try:
        ordenar_por = request.args.get('ordenar_por', 'data_coleta')
        ordem = request.args.get('ordem', 'desc')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        query = db.session.query(Preco, Produto, Estabelecimento).join(
            Produto, Preco.produto_id == Produto.id
        ).join(
            Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
        )
        
        # Ordenação
        if ordenar_por == 'preco':
            order_field = Preco.preco
        elif ordenar_por == 'produto':
            order_field = Produto.descricao
        elif ordenar_por == 'estabelecimento':
            order_field = Estabelecimento.nome
        else:
            order_field = Preco.data_coleta
        
        if ordem == 'asc':
            query = query.order_by(asc(order_field))
        else:
            query = query.order_by(desc(order_field))
        
        precos_paginados = query.paginate(page=page, per_page=per_page, error_out=False)
        
        resultado = []
        for preco, produto, estabelecimento in precos_paginados.items:
            resultado.append({
                'id': preco.id,
                'preco': float(preco.preco),
                'data_coleta': preco.data_coleta.isoformat(),
                'produto': {
                    'id': produto.id,
                    'descricao': produto.descricao,
                    'ean': produto.ean
                },
                'estabelecimento': {
                    'id': estabelecimento.id,
                    'nome': estabelecimento.nome,
                    'bairro': estabelecimento.bairro,
                    'cidade': estabelecimento.cidade
                }
            })
        
        return jsonify({
            'precos': resultado,
            'total': precos_paginados.total,
            'pages': precos_paginados.pages,
            'current_page': page,
            'ordenacao': {
                'campo': ordenar_por,
                'ordem': ordem
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na listagem ordenada: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/estatisticas-avancadas')
@limiter.limit("20 per minute")
@cache.cached(timeout=300)
def estatisticas_avancadas():
    """Estatísticas avançadas para gráficos"""
    try:
        # Top 10 produtos com mais preços
        top_produtos = db.session.query(
            Produto.descricao,
            func.count(Preco.id).label('total_precos'),
            func.min(Preco.preco).label('menor_preco'),
            func.max(Preco.preco).label('maior_preco'),
            func.avg(Preco.preco).label('preco_medio')
        ).join(
            Preco, Produto.id == Preco.produto_id
        ).group_by(
            Produto.id, Produto.descricao
        ).order_by(
            desc('total_precos')
        ).limit(10).all()
        
        # Top 10 estabelecimentos com mais preços
        top_estabelecimentos = db.session.query(
            Estabelecimento.nome,
            func.count(Preco.id).label('total_precos'),
            func.avg(Preco.preco).label('preco_medio')
        ).join(
            Preco, Estabelecimento.id == Preco.estabelecimento_id
        ).group_by(
            Estabelecimento.id, Estabelecimento.nome
        ).order_by(
            desc('total_precos')
        ).limit(10).all()
        
        # Variação de preços nos últimos 30 dias
        data_limite = datetime.utcnow() - timedelta(days=30)
        variacao_precos = db.session.query(
            func.date(Preco.data_coleta).label('data'),
            func.count(Preco.id).label('total_precos'),
            func.avg(Preco.preco).label('preco_medio')
        ).filter(
            Preco.data_coleta >= data_limite
        ).group_by(
            func.date(Preco.data_coleta)
        ).order_by('data').all()
        
        return jsonify({
            'top_produtos': [{
                'produto': p.descricao,
                'total_precos': p.total_precos,
                'menor_preco': float(p.menor_preco),
                'maior_preco': float(p.maior_preco),
                'preco_medio': float(p.preco_medio)
            } for p in top_produtos],
            'top_estabelecimentos': [{
                'estabelecimento': e.nome,
                'total_precos': e.total_precos,
                'preco_medio': float(e.preco_medio)
            } for e in top_estabelecimentos],
            'variacao_precos': [{
                'data': v.data.strftime('%Y-%m-%d'),
                'total_precos': v.total_precos,
                'preco_medio': float(v.preco_medio)
            } for v in variacao_precos]
        })
        
    except Exception as e:
        logger.error(f"Erro nas estatísticas avançadas: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)