from flask import Blueprint, request, jsonify, session, render_template
from models import db, Usuario
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validar_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route('/registro', methods=['GET'])
def registro_page():
    return render_template('registro.html')

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')
    
    if not email or not senha:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    
    usuario = Usuario.query.filter_by(email=email, ativo=True).first()
    
    if not usuario or not usuario.check_senha(senha):
        return jsonify({'error': 'Email ou senha inválidos'}), 401
    
    usuario.ultimo_login = datetime.utcnow()
    db.session.commit()
    
    session['user_id'] = usuario.id
    session['user_name'] = usuario.nome
    
    return jsonify({
        'success': True,
        'redirect': '/dashboard/adminlte',
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email
        }
    })

@auth_bp.route('/api/registro', methods=['POST'])
def registro():
    data = request.json
    nome = data.get('nome', '').strip()
    email = data.get('email', '').strip().lower()
    senha = data.get('senha', '')
    
    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios'}), 400
    
    if len(nome) < 2:
        return jsonify({'error': 'Nome deve ter pelo menos 2 caracteres'}), 400
    
    if not validar_email(email):
        return jsonify({'error': 'Email inválido'}), 400
    
    if len(senha) < 6:
        return jsonify({'error': 'Senha deve ter pelo menos 6 caracteres'}), 400
    
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 400
    
    usuario = Usuario(nome=nome, email=email)
    usuario.set_senha(senha)
    
    db.session.add(usuario)
    db.session.commit()
    
    session['user_id'] = usuario.id
    session['user_name'] = usuario.nome
    
    return jsonify({
        'success': True,
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email
        }
    }), 201

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/api/usuario-atual', methods=['GET'])
def usuario_atual():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    usuario = Usuario.query.get(session['user_id'])
    if not usuario or not usuario.ativo:
        session.clear()
        return jsonify({'error': 'Usuário inválido'}), 401
    
    return jsonify({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'is_admin': usuario.is_admin,
        'data_criacao': usuario.data_criacao.isoformat(),
        'ultimo_login': usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
    })

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Verifica status de autenticação do usuário"""
    if 'user_id' not in session:
        return jsonify({'authenticated': False, 'is_admin': False})
    
    usuario = Usuario.query.get(session['user_id'])
    if not usuario or not usuario.ativo:
        session.clear()
        return jsonify({'authenticated': False, 'is_admin': False})
    
    return jsonify({
        'authenticated': True,
        'is_admin': usuario.is_admin,
        'user_id': usuario.id,
        'user_name': usuario.nome
    })

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function