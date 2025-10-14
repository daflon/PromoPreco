from flask import Flask, request, jsonify, render_template, send_file, make_response, session
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
from models import db, Produto, Estabelecimento, Preco, Usuario, Favorito
from auth import auth_bp, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///promoprecco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
app.config['SECRET_KEY'] = 'promoprecco-secret-key-2024'

db.init_app(app)
app.register_blueprint(auth_bp)
cache = Cache(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



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
    return render_template('landing.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/cadastros')
def cadastros():
    return render_template('cadastros_adminlte.html')

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





# Administração
@app.route('/admin')
@login_required
def admin_panel():
    """Painel administrativo - apenas para administradores"""
    usuario_atual = Usuario.query.get(session.get('user_id'))
    if not usuario_atual or not usuario_atual.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    return render_template('admin_panel.html')

@app.route('/admin/usuarios', methods=['GET'])
@login_required
@limiter.limit("20 per minute")
def listar_usuarios_admin():
    """Lista usuários para administradores - dados anonimizados conforme LGPD"""
    usuario_atual = Usuario.query.get(session.get('user_id'))
    if not usuario_atual or not usuario_atual.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        usuarios = Usuario.query.all()
        resultado = []
        
        for u in usuarios:
            # Anonimização de dados conforme LGPD
            email_parts = u.email.split('@')
            email_anonimo = f"{email_parts[0][:2]}***@{email_parts[1]}" if len(email_parts) == 2 else "***@***"
            
            resultado.append({
                'id': u.id,
                'nome': u.nome[:2] + '***' if len(u.nome) > 2 else '***',  # Anonimizar nome
                'email': email_anonimo,  # Anonimizar email
                'data_criacao': u.data_criacao.strftime('%d/%m/%Y') if u.data_criacao else None,
                'ultimo_login': u.ultimo_login.strftime('%d/%m/%Y %H:%M') if u.ultimo_login else 'Nunca',
                'ativo': u.ativo,
                'is_admin': u.is_admin,
                'total_precos': u.precos.count(),
                'total_favoritos': u.favoritos.count()
            })
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/admin/usuarios/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_usuario_status(user_id):
    """Ativa/desativa usuário"""
    usuario_atual = Usuario.query.get(session.get('user_id'))
    if not usuario_atual or not usuario_atual.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    usuario = Usuario.query.get_or_404(user_id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    
    logger.info(f"Admin {usuario_atual.id} alterou status do usuário {user_id} para {'ativo' if usuario.ativo else 'inativo'}")
    return jsonify({'success': True, 'ativo': usuario.ativo})

@app.route('/admin/usuarios/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def toggle_usuario_admin(user_id):
    """Concede/remove privilégios de administrador"""
    usuario_atual = Usuario.query.get(session.get('user_id'))
    if not usuario_atual or not usuario_atual.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    if usuario_atual.id == user_id:
        return jsonify({'error': 'Não é possível alterar seus próprios privilégios'}), 400
    
    usuario = Usuario.query.get_or_404(user_id)
    usuario.is_admin = not usuario.is_admin
    db.session.commit()
    
    logger.info(f"Admin {usuario_atual.id} alterou privilégios admin do usuário {user_id} para {usuario.is_admin}")
    return jsonify({'success': True, 'is_admin': usuario.is_admin})

@app.route('/admin/stats', methods=['GET'])
@login_required
@cache.cached(timeout=300)
def admin_stats():
    """Estatísticas administrativas"""
    usuario_atual = Usuario.query.get(session.get('user_id'))
    if not usuario_atual or not usuario_atual.is_admin:
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        total_usuarios = Usuario.query.count()
        usuarios_ativos = Usuario.query.filter_by(ativo=True).count()
        usuarios_admin = Usuario.query.filter_by(is_admin=True).count()
        
        # Estatísticas dos últimos 30 dias
        data_limite = datetime.utcnow() - timedelta(days=30)
        
        precos_recentes = Preco.query.filter(Preco.data_coleta >= data_limite).count()
        usuarios_recentes = Usuario.query.filter(Usuario.data_criacao >= data_limite).count()
        
        return jsonify({
            'total_usuarios': total_usuarios,
            'usuarios_ativos': usuarios_ativos,
            'usuarios_admin': usuarios_admin,
            'precos_recentes': precos_recentes,
            'usuarios_recentes': usuarios_recentes
        })
        
    except Exception as e:
        logger.error(f"Erro ao carregar estatísticas admin: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

# Rotas de Relatórios

@app.route('/api/relatorio-vendas', methods=['GET'])
@limiter.limit("20 per minute")
@cache.cached(timeout=300)
def relatorio_vendas():
    """Relatório de análise de vendas por período"""
    try:
        dias = request.args.get('dias', 30, type=int)
        data_limite = datetime.utcnow() - timedelta(days=dias)
        
        # Estatísticas básicas
        total_produtos = Produto.query.count()
        total_estabelecimentos = Estabelecimento.query.count()
        total_precos = Preco.query.filter(Preco.data_coleta >= data_limite).count()
        
        # Dados mock para demonstração
        produtos_populares = []
        estabelecimentos_ativos = []
        evolucao_diaria = []
        
        # Se há dados, buscar informações reais
        if total_precos > 0:
            # Produtos com mais preços
            try:
                produtos_query = db.session.query(
                    Produto.id, Produto.descricao, func.count(Preco.id).label('total_precos')
                ).join(Preco).filter(
                    Preco.data_coleta >= data_limite
                ).group_by(Produto.id, Produto.descricao).order_by(
                    desc('total_precos')
                ).limit(5).all()
                
                produtos_populares = [{
                    'id': p.id,
                    'descricao': p.descricao,
                    'total_precos': p.total_precos
                } for p in produtos_query]
            except:
                pass
            
            # Estabelecimentos mais ativos
            try:
                estabelecimentos_query = db.session.query(
                    Estabelecimento.id, Estabelecimento.nome, func.count(Preco.id).label('total_precos')
                ).join(Preco).filter(
                    Preco.data_coleta >= data_limite
                ).group_by(Estabelecimento.id, Estabelecimento.nome).order_by(
                    desc('total_precos')
                ).limit(5).all()
                
                estabelecimentos_ativos = [{
                    'id': e.id,
                    'nome': e.nome,
                    'total_precos': e.total_precos
                } for e in estabelecimentos_query]
            except:
                pass
        
        # Dados padrão se não houver dados suficientes
        if not produtos_populares:
            produtos_populares = [{
                'id': 1,
                'descricao': 'Nenhum produto encontrado',
                'total_precos': 0
            }]
        
        if not estabelecimentos_ativos:
            estabelecimentos_ativos = [{
                'id': 1,
                'nome': 'Nenhum estabelecimento encontrado',
                'total_precos': 0
            }]
        
        evolucao_diaria = [{
            'data': datetime.now().strftime('%Y-%m-%d'),
            'total': total_precos
        }]
        
        return jsonify({
            'produtos_populares': produtos_populares,
            'estabelecimentos_ativos': estabelecimentos_ativos,
            'evolucao_diaria': evolucao_diaria
        })
        
    except Exception as e:
        logger.error(f"Erro no relatório de vendas: {str(e)}")
        return jsonify({
            'produtos_populares': [{'id': 1, 'descricao': 'Erro ao carregar', 'total_precos': 0}],
            'estabelecimentos_ativos': [{'id': 1, 'nome': 'Erro ao carregar', 'total_precos': 0}],
            'evolucao_diaria': [{'data': datetime.now().strftime('%Y-%m-%d'), 'total': 0}]
        })



@app.route('/api/relatorio-comparativo', methods=['GET'])
@limiter.limit("20 per minute")
@cache.cached(timeout=300)
def relatorio_comparativo():
    """Relatório comparativo de preços entre estabelecimentos"""
    try:
        produto_id = request.args.get('produto_id', type=int)
        if not produto_id:
            return jsonify({'error': 'produto_id é obrigatório'}), 400
            
        produto = Produto.query.get_or_404(produto_id)
        
        # Preços atuais por estabelecimento
        precos_atuais = db.session.query(
            Estabelecimento.nome,
            Estabelecimento.bairro,
            Preco.preco,
            Preco.data_coleta
        ).join(Preco).filter(
            Preco.produto_id == produto_id
        ).order_by(desc(Preco.data_coleta)).all()
        
        # Agrupar por estabelecimento (pegar o mais recente)
        estabelecimentos = {}
        for nome, bairro, preco, data in precos_atuais:
            key = f"{nome} - {bairro}"
            if key not in estabelecimentos:
                estabelecimentos[key] = {
                    'estabelecimento': nome,
                    'bairro': bairro,
                    'preco': float(preco),
                    'data_coleta': data.strftime('%d/%m/%Y %H:%M')
                }
        
        dados = list(estabelecimentos.values())
        dados.sort(key=lambda x: x['preco'])
        
        # Calcular estatísticas
        precos_valores = [d['preco'] for d in dados]
        if precos_valores:
            menor_preco = min(precos_valores)
            maior_preco = max(precos_valores)
            preco_medio = sum(precos_valores) / len(precos_valores)
            economia_maxima = maior_preco - menor_preco
        else:
            menor_preco = maior_preco = preco_medio = economia_maxima = 0
        
        return jsonify({
            'produto': {
                'id': produto.id,
                'descricao': produto.descricao,
                'ean': produto.ean
            },
            'estatisticas': {
                'menor_preco': menor_preco,
                'maior_preco': maior_preco,
                'preco_medio': preco_medio,
                'economia_maxima': economia_maxima,
                'total_estabelecimentos': len(dados)
            },
            'precos': dados
        })
        
    except Exception as e:
        logger.error(f"Erro no relatório comparativo: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

# Funções auxiliares para exportação
def gerar_csv(dados, filename):
    """Gera arquivo CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=dados[0].keys() if dados else [])
    writer.writeheader()
    writer.writerows(dados)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def gerar_excel(dados, filename):
    """Gera arquivo Excel"""
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    if dados:
        # Cabeçalhos
        headers = list(dados[0].keys())
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Dados
        for row, item in enumerate(dados, 1):
            for col, header in enumerate(headers):
                worksheet.write(row, col, item[header])
    
    workbook.close()
    output.seek(0)
    
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response

def gerar_pdf(dados, titulo):
    """Gera arquivo PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph(titulo, styles['Title'])
    elements.append(title)
    
    if dados:
        # Tabela
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
    response.headers['Content-Disposition'] = f'attachment; filename={titulo.replace(" ", "_")}.pdf'
    return response

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
    
    usuario_id = session.get('user_id')
    
    preco = Preco(
        produto_id=data['produto_id'],
        estabelecimento_id=data['estabelecimento_id'],
        preco=preco_valor,
        usuario_id=usuario_id
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
    return render_template('relatorios_novo.html')

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

# Favoritos
@app.route('/api/favoritos', methods=['GET'])
@login_required
def listar_favoritos():
    """Lista favoritos do usuário logado"""
    try:
        usuario_id = session['user_id']
        favoritos = db.session.query(Favorito, Produto).join(
            Produto, Favorito.produto_id == Produto.id
        ).filter(Favorito.usuario_id == usuario_id).all()
        
        resultado = []
        for favorito, produto in favoritos:
            # Buscar menor preço do produto
            menor_preco = db.session.query(Preco, Estabelecimento).join(
                Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
            ).filter(Preco.produto_id == produto.id).order_by(Preco.preco).first()
            
            item = {
                'id': favorito.id,
                'produto': {
                    'id': produto.id,
                    'descricao': produto.descricao,
                    'ean': produto.ean
                },
                'data_criacao': favorito.data_criacao.isoformat()
            }
            
            if menor_preco:
                preco, estabelecimento = menor_preco
                item['menor_preco'] = {
                    'preco': float(preco.preco),
                    'estabelecimento': estabelecimento.nome,
                    'data_coleta': preco.data_coleta.isoformat()
                }
            
            resultado.append(item)
        
        return jsonify(resultado)
        
    except Exception as e:
        logger.error(f"Erro ao listar favoritos: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/favoritos', methods=['POST'])
@login_required
def adicionar_favorito():
    """Adiciona produto aos favoritos"""
    try:
        data = request.json
        produto_id = data.get('produto_id')
        
        if not produto_id:
            return jsonify({'error': 'ID do produto é obrigatório'}), 400
        
        produto = Produto.query.get_or_404(produto_id)
        usuario_id = session['user_id']
        
        # Verificar se já existe
        favorito_existente = Favorito.query.filter_by(
            usuario_id=usuario_id, produto_id=produto_id
        ).first()
        
        if favorito_existente:
            return jsonify({'error': 'Produto já está nos favoritos'}), 400
        
        favorito = Favorito(usuario_id=usuario_id, produto_id=produto_id)
        db.session.add(favorito)
        db.session.commit()
        
        return jsonify({'id': favorito.id, 'message': 'Produto adicionado aos favoritos'}), 201
        
    except Exception as e:
        logger.error(f"Erro ao adicionar favorito: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/favoritos/<int:id>', methods=['DELETE'])
@login_required
def remover_favorito(id):
    """Remove produto dos favoritos"""
    try:
        usuario_id = session['user_id']
        favorito = Favorito.query.filter_by(id=id, usuario_id=usuario_id).first_or_404()
        
        db.session.delete(favorito)
        db.session.commit()
        
        return jsonify({'message': 'Produto removido dos favoritos'})
        
    except Exception as e:
        logger.error(f"Erro ao remover favorito: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

# Rotas de compatibilidade para favoritos
@app.route('/favoritos', methods=['POST'])
@login_required
def adicionar_favorito_compat():
    """Rota de compatibilidade para adicionar favorito"""
    return adicionar_favorito()

# Listas de Compras
@app.route('/api/listas', methods=['GET'])
@login_required
def listar_listas():
    """Lista as listas de compras do usuário"""
    try:
        usuario_id = session['user_id']
        # Por simplicidade, vamos usar favoritos como "lista padrão"
        favoritos = db.session.query(Favorito, Produto).join(
            Produto, Favorito.produto_id == Produto.id
        ).filter(Favorito.usuario_id == usuario_id).all()
        
        lista_padrao = {
            'id': 1,
            'nome': 'Lista Padrão',
            'produtos': []
        }
        
        for favorito, produto in favoritos:
            lista_padrao['produtos'].append({
                'id': produto.id,
                'descricao': produto.descricao,
                'ean': produto.ean
            })
        
        return jsonify([lista_padrao])
        
    except Exception as e:
        logger.error(f"Erro ao listar listas: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/listas/comparar', methods=['POST'])
@login_required
def comparar_lista():
    """Compara preços de uma lista de produtos"""
    try:
        data = request.json
        produtos_ids = data.get('produtos', [])
        
        if not produtos_ids:
            return jsonify({'error': 'Lista vazia'}), 400
        
        resultado = []
        total_menor = 0
        total_maior = 0
        
        for produto_id in produtos_ids:
            produto = Produto.query.get(produto_id)
            if not produto:
                continue
                
            precos = db.session.query(Preco, Estabelecimento).join(
                Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
            ).filter(Preco.produto_id == produto_id).order_by(Preco.preco).all()
            
            if precos:
                menor_preco = precos[0][0].preco
                maior_preco = precos[-1][0].preco
                total_menor += menor_preco
                total_maior += maior_preco
                
                resultado.append({
                    'produto': {
                        'id': produto.id,
                        'descricao': produto.descricao
                    },
                    'menor_preco': float(menor_preco),
                    'maior_preco': float(maior_preco),
                    'estabelecimento_menor': precos[0][1].nome,
                    'estabelecimento_maior': precos[-1][1].nome
                })
        
        return jsonify({
            'produtos': resultado,
            'total_menor': float(total_menor),
            'total_maior': float(total_maior),
            'economia': float(total_maior - total_menor)
        })
        
    except Exception as e:
        logger.error(f"Erro ao comparar lista: {str(e)}")
        return jsonify({'error': 'Erro interno'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)