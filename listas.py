from flask import Blueprint, request, jsonify, session, render_template
from models import db, ListaCompras, ItemLista, Produto, Preco, Estabelecimento
from auth import login_required
from sqlalchemy import func

listas_bp = Blueprint('listas', __name__)

@listas_bp.route('/listas', methods=['GET'])
@login_required
def listas_page():
    return render_template('listas_adminlte.html')

@listas_bp.route('/api/listas', methods=['GET'])
@login_required
def listar_listas():
    user_id = session['user_id']
    listas = ListaCompras.query.filter_by(usuario_id=user_id, ativa=True).order_by(ListaCompras.data_criacao.desc()).all()
    
    resultado = []
    for lista in listas:
        total_itens = ItemLista.query.filter_by(lista_id=lista.id).count()
        itens_comprados = ItemLista.query.filter_by(lista_id=lista.id, comprado=True).count()
        
        resultado.append({
            'id': lista.id,
            'nome': lista.nome,
            'data_criacao': lista.data_criacao.isoformat(),
            'total_itens': total_itens,
            'itens_comprados': itens_comprados,
            'progresso': round((itens_comprados / total_itens * 100) if total_itens > 0 else 0, 1)
        })
    
    return jsonify(resultado)

@listas_bp.route('/api/listas', methods=['POST'])
@login_required
def criar_lista():
    data = request.json
    nome = data.get('nome', '').strip()
    
    if not nome:
        return jsonify({'error': 'Nome da lista é obrigatório'}), 400
    
    if len(nome) < 2:
        return jsonify({'error': 'Nome deve ter pelo menos 2 caracteres'}), 400
    
    lista = ListaCompras(nome=nome, usuario_id=session['user_id'])
    db.session.add(lista)
    db.session.commit()
    
    return jsonify({'id': lista.id, 'nome': lista.nome}), 201

@listas_bp.route('/api/listas/<int:lista_id>', methods=['GET'])
@login_required
def obter_lista(lista_id):
    lista = ListaCompras.query.filter_by(id=lista_id, usuario_id=session['user_id'], ativa=True).first()
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    itens = db.session.query(ItemLista, Produto).join(
        Produto, ItemLista.produto_id == Produto.id
    ).filter(ItemLista.lista_id == lista_id).all()
    
    resultado = {
        'id': lista.id,
        'nome': lista.nome,
        'data_criacao': lista.data_criacao.isoformat(),
        'itens': []
    }
    
    for item, produto in itens:
        # Buscar menor preço do produto
        menor_preco = db.session.query(func.min(Preco.preco)).filter_by(produto_id=produto.id).scalar()
        
        resultado['itens'].append({
            'id': item.id,
            'produto_id': produto.id,
            'produto_nome': produto.descricao,
            'quantidade': item.quantidade,
            'comprado': item.comprado,
            'menor_preco': float(menor_preco) if menor_preco else None
        })
    
    return jsonify(resultado)

@listas_bp.route('/api/listas/<int:lista_id>/itens', methods=['POST'])
@login_required
def adicionar_item(lista_id):
    lista = ListaCompras.query.filter_by(id=lista_id, usuario_id=session['user_id'], ativa=True).first()
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    data = request.json
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade', 1)
    
    if not produto_id:
        return jsonify({'error': 'Produto é obrigatório'}), 400
    
    if quantidade < 1:
        return jsonify({'error': 'Quantidade deve ser maior que zero'}), 400
    
    # Verificar se produto existe
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({'error': 'Produto não encontrado'}), 404
    
    # Verificar se item já existe na lista
    item_existente = ItemLista.query.filter_by(lista_id=lista_id, produto_id=produto_id).first()
    if item_existente:
        item_existente.quantidade += quantidade
        db.session.commit()
        return jsonify({'id': item_existente.id, 'quantidade': item_existente.quantidade})
    
    item = ItemLista(lista_id=lista_id, produto_id=produto_id, quantidade=quantidade)
    db.session.add(item)
    db.session.commit()
    
    return jsonify({'id': item.id, 'quantidade': item.quantidade}), 201

@listas_bp.route('/api/listas/<int:lista_id>/itens/<int:item_id>', methods=['PUT'])
@login_required
def atualizar_item(lista_id, item_id):
    lista = ListaCompras.query.filter_by(id=lista_id, usuario_id=session['user_id'], ativa=True).first()
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    item = ItemLista.query.filter_by(id=item_id, lista_id=lista_id).first()
    if not item:
        return jsonify({'error': 'Item não encontrado'}), 404
    
    data = request.json
    if 'quantidade' in data:
        quantidade = data['quantidade']
        if quantidade < 1:
            return jsonify({'error': 'Quantidade deve ser maior que zero'}), 400
        item.quantidade = quantidade
    
    if 'comprado' in data:
        item.comprado = bool(data['comprado'])
    
    db.session.commit()
    return jsonify({'success': True})

@listas_bp.route('/api/listas/<int:lista_id>/itens/<int:item_id>', methods=['DELETE'])
@login_required
def remover_item(lista_id, item_id):
    lista = ListaCompras.query.filter_by(id=lista_id, usuario_id=session['user_id'], ativa=True).first()
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    item = ItemLista.query.filter_by(id=item_id, lista_id=lista_id).first()
    if not item:
        return jsonify({'error': 'Item não encontrado'}), 404
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

@listas_bp.route('/api/listas/<int:lista_id>/comparar', methods=['GET'])
@login_required
def comparar_lista(lista_id):
    lista = ListaCompras.query.filter_by(id=lista_id, usuario_id=session['user_id'], ativa=True).first()
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    itens = db.session.query(ItemLista, Produto).join(
        Produto, ItemLista.produto_id == Produto.id
    ).filter(ItemLista.lista_id == lista_id).all()
    
    # Agrupar preços por estabelecimento
    estabelecimentos_totais = {}
    
    for item, produto in itens:
        precos = db.session.query(Preco, Estabelecimento).join(
            Estabelecimento, Preco.estabelecimento_id == Estabelecimento.id
        ).filter(Preco.produto_id == produto.id).all()
        
        for preco, estabelecimento in precos:
            est_id = estabelecimento.id
            if est_id not in estabelecimentos_totais:
                estabelecimentos_totais[est_id] = {
                    'estabelecimento': {
                        'id': estabelecimento.id,
                        'nome': estabelecimento.nome,
                        'bairro': estabelecimento.bairro,
                        'cidade': estabelecimento.cidade
                    },
                    'total': 0,
                    'itens_encontrados': 0,
                    'total_itens': len(itens)
                }
            
            estabelecimentos_totais[est_id]['total'] += float(preco.preco) * item.quantidade
            estabelecimentos_totais[est_id]['itens_encontrados'] += 1
    
    # Ordenar por menor total
    resultado = sorted(estabelecimentos_totais.values(), key=lambda x: x['total'])
    
    return jsonify({
        'lista': {
            'id': lista.id,
            'nome': lista.nome
        },
        'comparacao': resultado
    })