#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados e verificar se as APIs estão funcionando
"""

import requests
import json
from datetime import datetime

def testar_api():
    base_url = "http://localhost:5000"
    
    print("=== TESTE DE CONEXÃO COM A API ===")
    print(f"Testando conexão com: {base_url}")
    print(f"Horário: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Teste 1: Status da API
    try:
        response = requests.get(f"{base_url}/api", timeout=5)
        if response.status_code == 200:
            print("[OK] API está rodando")
            print(f"   Resposta: {response.json()}")
        else:
            print(f"[ERRO] API retornou status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("[ERRO] Erro de conexão - Servidor não está rodando")
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False
    
    # Teste 2: Produtos
    try:
        response = requests.get(f"{base_url}/produtos", timeout=10)
        if response.status_code == 200:
            produtos = response.json()
            print(f"[OK] Endpoint /produtos funcionando")
            print(f"   Total de produtos: {len(produtos)}")
            if produtos:
                print(f"   Exemplo: {produtos[0]}")
            else:
                print("   [AVISO] Nenhum produto cadastrado")
        else:
            print(f"[ERRO] /produtos retornou status {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"[ERRO] Erro ao testar /produtos: {e}")
    
    # Teste 3: Categorias
    try:
        response = requests.get(f"{base_url}/categorias", timeout=10)
        if response.status_code == 200:
            categorias = response.json()
            print(f"[OK] Endpoint /categorias funcionando")
            print(f"   Total de categorias: {len(categorias)}")
            if categorias:
                print(f"   Exemplo: {categorias[0]}")
            else:
                print("   [AVISO] Nenhuma categoria cadastrada")
        else:
            print(f"[ERRO] /categorias retornou status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] Erro ao testar /categorias: {e}")
    
    # Teste 4: Estabelecimentos
    try:
        response = requests.get(f"{base_url}/estabelecimentos", timeout=10)
        if response.status_code == 200:
            estabelecimentos = response.json()
            print(f"[OK] Endpoint /estabelecimentos funcionando")
            print(f"   Total de estabelecimentos: {len(estabelecimentos)}")
            if estabelecimentos:
                print(f"   Exemplo: {estabelecimentos[0]}")
            else:
                print("   [AVISO] Nenhum estabelecimento cadastrado")
        else:
            print(f"[ERRO] /estabelecimentos retornou status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] Erro ao testar /estabelecimentos: {e}")
    
    # Teste 5: Página principal
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("[OK] Página principal carregando")
        else:
            print(f"[ERRO] Página principal retornou status {response.status_code}")
    except Exception as e:
        print(f"[ERRO] Erro ao testar página principal: {e}")
    
    print("-" * 50)
    print("=== FIM DOS TESTES ===")
    return True

def verificar_banco():
    """Verifica se o banco de dados existe e tem dados"""
    import os
    import sqlite3
    
    print("\n=== VERIFICAÇÃO DO BANCO DE DADOS ===")
    
    db_path = "instance/promoprecco.db"
    if not os.path.exists(db_path):
        print("[ERRO] Banco de dados não encontrado!")
        print(f"   Procurando em: {os.path.abspath(db_path)}")
        return False
    
    print(f"[OK] Banco de dados encontrado: {os.path.abspath(db_path)}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        print(f"   Tabelas encontradas: {[t[0] for t in tabelas]}")
        
        # Contar registros
        for tabela in ['produto', 'categoria', 'estabelecimento', 'preco']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"   {tabela}: {count} registros")
            except sqlite3.OperationalError:
                print(f"   {tabela}: tabela não existe")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao acessar banco: {e}")
        return False

if __name__ == "__main__":
    print("DIAGNÓSTICO DO SISTEMA PROMOPREÇO")
    print("=" * 60)
    
    # Verificar banco primeiro
    verificar_banco()
    
    # Testar API
    testar_api()
    
    print("\n[DICAS] PARA RESOLVER PROBLEMAS:")
    print("1. Certifique-se que o servidor Flask está rodando: python app.py")
    print("2. Verifique se não há erros no console do servidor")
    print("3. Se o banco estiver vazio, execute: python Testes/popular_dados_completos.py")
    print("4. Verifique se todas as dependências estão instaladas: pip install -r requirements.txt")