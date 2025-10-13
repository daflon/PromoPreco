#!/usr/bin/env python3
"""
Script de debug para testar as rotas individualmente
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def testar_api():
    """Testa se a API está funcionando"""
    try:
        response = requests.get(f'{BASE_URL}/api')
        print(f"✅ API Status: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        return False

def testar_produto():
    """Testa criação de produto"""
    data = {
        'descricao': 'Teste Produto',
        'ean': '1234567890123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/produtos', json=data)
        print(f"📦 Produto - Status: {response.status_code}")
        print(f"📦 Produto - Response: {response.text}")
        
        if response.status_code == 201:
            return response.json()['id']
        return None
    except Exception as e:
        print(f"❌ Erro ao criar produto: {e}")
        return None

def testar_estabelecimento():
    """Testa criação de estabelecimento"""
    data = {
        'nome': 'Teste Mercado',
        'cnpj': '12345678901234',
        'bairro': 'Centro',
        'cidade': 'São Paulo'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/estabelecimentos', json=data)
        print(f"🏪 Estabelecimento - Status: {response.status_code}")
        print(f"🏪 Estabelecimento - Response: {response.text}")
        
        if response.status_code == 201:
            return response.json()['id']
        return None
    except Exception as e:
        print(f"❌ Erro ao criar estabelecimento: {e}")
        return None

def testar_preco(produto_id, estabelecimento_id):
    """Testa criação de preço"""
    data = {
        'produto_id': produto_id,
        'estabelecimento_id': estabelecimento_id,
        'preco': 10.50
    }
    
    try:
        response = requests.post(f'{BASE_URL}/precos', json=data)
        print(f"💰 Preço - Status: {response.status_code}")
        print(f"💰 Preço - Response: {response.text}")
        
        if response.status_code == 201:
            return response.json()['id']
        return None
    except Exception as e:
        print(f"❌ Erro ao criar preço: {e}")
        return None

def main():
    print("🔍 Testando rotas individualmente...")
    print("=" * 50)
    
    # Teste 1: API
    if not testar_api():
        return
    
    # Teste 2: Produto
    produto_id = testar_produto()
    if not produto_id:
        print("❌ Falha ao criar produto - parando testes")
        return
    
    # Teste 3: Estabelecimento
    estabelecimento_id = testar_estabelecimento()
    if not estabelecimento_id:
        print("❌ Falha ao criar estabelecimento - parando testes")
        return
    
    # Teste 4: Preço
    preco_id = testar_preco(produto_id, estabelecimento_id)
    if not preco_id:
        print("❌ Falha ao criar preço")
        return
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes passaram!")
    print(f"📦 Produto ID: {produto_id}")
    print(f"🏪 Estabelecimento ID: {estabelecimento_id}")
    print(f"💰 Preço ID: {preco_id}")

if __name__ == '__main__':
    main()