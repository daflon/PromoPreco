#!/usr/bin/env python3
"""
Teste simples das rotas da API
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def testar_api():
    """Testa se a API está funcionando"""
    try:
        response = requests.get(f'{BASE_URL}/api')
        print(f"API Status: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"Erro na API: {e}")
        return False

def testar_produtos():
    """Testa listagem de produtos"""
    try:
        response = requests.get(f'{BASE_URL}/produtos')
        print(f"Produtos - Status: {response.status_code}")
        if response.status_code == 200:
            produtos = response.json()
            print(f"Total de produtos: {len(produtos)}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        return False

def testar_categorias():
    """Testa listagem de categorias"""
    try:
        response = requests.get(f'{BASE_URL}/categorias')
        print(f"Categorias - Status: {response.status_code}")
        if response.status_code == 200:
            categorias = response.json()
            print(f"Total de categorias: {len(categorias)}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao listar categorias: {e}")
        return False

def testar_estabelecimentos():
    """Testa listagem de estabelecimentos"""
    try:
        response = requests.get(f'{BASE_URL}/estabelecimentos')
        print(f"Estabelecimentos - Status: {response.status_code}")
        if response.status_code == 200:
            estabelecimentos = response.json()
            print(f"Total de estabelecimentos: {len(estabelecimentos)}")
            return True
        else:
            print(f"Erro: {response.text}")
            return False
    except Exception as e:
        print(f"Erro ao listar estabelecimentos: {e}")
        return False

def testar_cadastro_produto():
    """Testa cadastro de produto"""
    data = {
        'descricao': 'Produto Teste Debug',
        'ean': '1234567890123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/produtos', json=data)
        print(f"Cadastro Produto - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            return response.json()['id']
        return None
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return None

def main():
    print("Testando rotas da API...")
    print("=" * 50)
    
    # Teste 1: API
    if not testar_api():
        print("API nao esta funcionando!")
        return
    
    # Teste 2: Listagens
    print("\nTestando listagens:")
    testar_produtos()
    testar_categorias()
    testar_estabelecimentos()
    
    # Teste 3: Cadastro
    print("\nTestando cadastro:")
    produto_id = testar_cadastro_produto()
    
    if produto_id:
        print(f"Produto criado com ID: {produto_id}")
    else:
        print("Falha ao criar produto")

if __name__ == '__main__':
    main()