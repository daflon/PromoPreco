#!/usr/bin/env python3
"""
Script para popular o banco com dados completos de teste:
- 100 produtos
- 20 estabelecimentos  
- Preços para cada produto em cada estabelecimento (2000 preços)
"""

import requests
import random
from datetime import datetime

BASE_URL = 'http://localhost:5000'

# Categorias de produtos para gerar nomes realistas
CATEGORIAS = {
    'Alimentos': ['Arroz', 'Feijão', 'Macarrão', 'Açúcar', 'Sal', 'Óleo', 'Vinagre', 'Farinha', 'Café', 'Leite'],
    'Bebidas': ['Refrigerante', 'Suco', 'Água', 'Cerveja', 'Vinho', 'Energético', 'Isotônico', 'Chá', 'Água de Coco'],
    'Higiene': ['Sabonete', 'Shampoo', 'Pasta de Dente', 'Desodorante', 'Papel Higiênico', 'Absorvente'],
    'Limpeza': ['Detergente', 'Sabão em Pó', 'Amaciante', 'Desinfetante', 'Álcool', 'Água Sanitária'],
    'Padaria': ['Pão', 'Bolo', 'Biscoito', 'Torrada', 'Rosca', 'Croissant'],
    'Laticínios': ['Queijo', 'Iogurte', 'Manteiga', 'Requeijão', 'Cream Cheese', 'Leite Condensado'],
    'Carnes': ['Frango', 'Carne Bovina', 'Peixe', 'Linguiça', 'Presunto', 'Mortadela'],
    'Frutas': ['Banana', 'Maçã', 'Laranja', 'Uva', 'Mamão', 'Abacaxi', 'Melancia', 'Pêra'],
    'Verduras': ['Alface', 'Tomate', 'Cebola', 'Batata', 'Cenoura', 'Abobrinha', 'Pepino'],
    'Congelados': ['Pizza', 'Hambúrguer', 'Nuggets', 'Sorvete', 'Açaí', 'Peixe Congelado']
}

MARCAS = ['Nestlé', 'Unilever', 'Sadia', 'Perdigão', 'Tio João', 'Camil', 'Liza', 'Omo', 'Ariel', 'Dove', 'Garoto', 'Lacta']
TAMANHOS = ['500g', '1kg', '2kg', '5kg', '1L', '2L', '500ml', '350ml', '200g', '100g', 'Unidade', 'Pacote']

REDES = ['Extra', 'Carrefour', 'Pão de Açúcar', 'Atacadão', 'Big', 'Walmart', 'Assaí', 'Makro', 'Sam\'s Club', 'BH']
BAIRROS = ['Centro', 'Vila Madalena', 'Jardins', 'Mooca', 'Ipiranga', 'Tatuapé', 'Liberdade', 'Vila Olímpia', 'Brooklin', 'Pinheiros']
CIDADES = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador', 'Fortaleza', 'Recife', 'Porto Alegre']

def gerar_produtos(quantidade=100):
    """Gera lista de produtos únicos"""
    produtos = []
    ean_base = 7891000000000
    
    for i in range(quantidade):
        categoria = random.choice(list(CATEGORIAS.keys()))
        produto_base = random.choice(CATEGORIAS[categoria])
        marca = random.choice(MARCAS)
        tamanho = random.choice(TAMANHOS)
        
        descricao = f"{produto_base} {marca} {tamanho}"
        ean = str(ean_base + i)
        
        produtos.append({
            'descricao': descricao,
            'ean': ean
        })
    
    return produtos

def gerar_estabelecimentos(quantidade=20):
    """Gera lista de estabelecimentos únicos"""
    estabelecimentos = []
    cnpj_base = 10000000000100
    
    for i in range(quantidade):
        rede = random.choice(REDES)
        bairro = random.choice(BAIRROS)
        cidade = random.choice(CIDADES)
        
        nome = f"{rede} {bairro}"
        cnpj = str(cnpj_base + i)
        
        estabelecimentos.append({
            'nome': nome,
            'cnpj': cnpj,
            'bairro': bairro,
            'cidade': cidade
        })
    
    return estabelecimentos

def criar_entidade(endpoint, data, nome_entidade):
    """Cria uma entidade via API"""
    try:
        print(f"🔄 Criando {nome_entidade}: {data}")
        response = requests.post(f'{BASE_URL}/{endpoint}', json=data)
        print(f"📡 Status: {response.status_code}, Response: {response.text}")
        if response.status_code == 201:
            return response.json()['id']
        else:
            print(f"❌ Erro ao criar {nome_entidade}: Status {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro de conexão ao criar {nome_entidade}: {e}")
        return None

def criar_preco(produto_id, estabelecimento_id, preco_base):
    """Cria preço com variação realista"""
    variacao = random.uniform(0.7, 1.4)  # Variação de -30% a +40%
    preco = round(preco_base * variacao, 2)
    
    data = {
        'produto_id': produto_id,
        'estabelecimento_id': estabelecimento_id,
        'preco': preco
    }
    
    return criar_entidade('precos', data, 'preço')

def main():
    print("🚀 Populando banco com dados completos de teste...")
    print("=" * 60)
    
    # Verificar API
    try:
        response = requests.get(f'{BASE_URL}/api')
        if response.status_code != 200:
            print("❌ API não está respondendo. Execute: python app.py")
            return
    except:
        print("❌ Erro ao conectar. Certifique-se que o Flask está rodando.")
        return
    
    # Gerar dados
    print("📝 Gerando dados...")
    produtos_data = gerar_produtos(100)
    estabelecimentos_data = gerar_estabelecimentos(20)
    
    # Criar produtos
    print("\n📦 Criando 100 produtos...")
    produtos_ids = []
    for i, produto in enumerate(produtos_data, 1):
        produto_id = criar_entidade('produtos', produto, 'produto')
        if produto_id:
            produtos_ids.append(produto_id)
            if i % 10 == 0:
                print(f"   ✅ {i}/100 produtos criados")
    
    # Criar estabelecimentos
    print("\n🏪 Criando 20 estabelecimentos...")
    estabelecimentos_ids = []
    for i, estabelecimento in enumerate(estabelecimentos_data, 1):
        estabelecimento_id = criar_entidade('estabelecimentos', estabelecimento, 'estabelecimento')
        if estabelecimento_id:
            estabelecimentos_ids.append(estabelecimento_id)
            print(f"   ✅ {i}/20 estabelecimentos criados")
    
    # Criar preços (cada produto em cada estabelecimento)
    print("\n💰 Criando preços (100 produtos × 20 estabelecimentos = 2000 preços)...")
    precos_criados = 0
    total_precos = len(produtos_ids) * len(estabelecimentos_ids)
    
    # Preços base por categoria (estimativa realista)
    precos_base = {
        'Alimentos': 8.50, 'Bebidas': 4.20, 'Higiene': 12.90, 'Limpeza': 6.80,
        'Padaria': 3.50, 'Laticínios': 7.90, 'Carnes': 25.90, 'Frutas': 5.40,
        'Verduras': 4.20, 'Congelados': 15.90
    }
    
    for i, produto_id in enumerate(produtos_ids):
        # Determinar preço base pela descrição do produto
        produto_desc = produtos_data[i]['descricao']
        preco_base = 10.00  # padrão
        
        for categoria, preco in precos_base.items():
            if any(item in produto_desc for item in CATEGORIAS[categoria]):
                preco_base = preco
                break
        
        for estabelecimento_id in estabelecimentos_ids:
            preco_id = criar_preco(produto_id, estabelecimento_id, preco_base)
            if preco_id:
                precos_criados += 1
        
        if (i + 1) % 10 == 0:
            print(f"   ✅ {precos_criados}/{total_precos} preços criados ({i+1}/100 produtos processados)")
    
    print("\n" + "=" * 60)
    print("🎉 População completa!")
    print(f"📊 Resumo:")
    print(f"   • Produtos: {len(produtos_ids)}")
    print(f"   • Estabelecimentos: {len(estabelecimentos_ids)}")
    print(f"   • Preços: {precos_criados}")
    print(f"\n🌐 Acesse:")
    print(f"   • Sistema: {BASE_URL}")
    print(f"   • Dashboard: {BASE_URL}/dashboard")

if __name__ == '__main__':
    main()