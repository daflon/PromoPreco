#!/usr/bin/env python3
"""
Script para testar todas as APIs do sistema PromoPreço
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def testar_api(endpoint, nome):
    """Testa um endpoint da API"""
    try:
        print(f"\nTestando {nome}...")
        response = requests.get(f'{BASE_URL}{endpoint}')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                if 'total' in data:
                    print(f"   Total de registros: {data['total']}")
                if 'precos' in data:
                    print(f"   Preços retornados: {len(data['precos'])}")
                if 'produtos' in data:
                    print(f"   Produtos retornados: {len(data)}")
            elif isinstance(data, list):
                print(f"   Registros retornados: {len(data)}")
            
            # Mostra uma amostra dos dados
            if isinstance(data, dict) and 'precos' in data and data['precos']:
                print(f"   Exemplo: {data['precos'][0]}")
            elif isinstance(data, list) and data:
                print(f"   Exemplo: {data[0]}")
        else:
            print(f"   Erro: {response.text}")
            
    except Exception as e:
        print(f"   Erro de conexao: {e}")

def main():
    print("Testando todas as APIs do PromoPreco")
    print("=" * 50)
    
    # Testa API básica
    testar_api('/api', 'API Status')
    
    # Testa produtos
    testar_api('/produtos', 'Produtos')
    
    # Testa estabelecimentos
    testar_api('/estabelecimentos', 'Estabelecimentos')
    
    # Testa preços (original)
    testar_api('/precos', 'Preços (original)')
    
    # Testa preços detalhados
    testar_api('/precos/detalhados', 'Preços Detalhados')
    
    # Testa dashboard stats
    testar_api('/dashboard/stats', 'Dashboard Stats')
    
    # Testa comparação (se houver produtos)
    try:
        response = requests.get(f'{BASE_URL}/produtos')
        if response.status_code == 200:
            produtos = response.json()
            if produtos:
                produto_id = produtos[0]['id']
                testar_api(f'/comparar/{produto_id}', f'Comparação de Preços (Produto {produto_id})')
    except:
        print("\nTestando Comparacao de Precos...")
        print("   Nao foi possivel testar - sem produtos disponiveis")
    
    print("\n" + "=" * 50)
    print("Teste concluido!")

if __name__ == '__main__':
    main()