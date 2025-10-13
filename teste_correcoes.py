#!/usr/bin/env python3
"""
Teste das correções aplicadas ao PromoPreço
Verifica se todas as funcionalidades estão funcionando conforme as regras
"""

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def testar_api():
    """Testa se a API está funcionando"""
    try:
        response = requests.get(f'{BASE_URL}/api')
        if response.status_code == 200:
            print("✅ API funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def testar_produtos():
    """Testa CRUD de produtos"""
    print("\n🧪 Testando produtos...")
    
    # Criar produto
    produto_data = {
        "descricao": "Teste Produto",
        "ean": "1234567890123"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/produtos', json=produto_data)
        if response.status_code == 201:
            produto_id = response.json()['id']
            print(f"✅ Produto criado com ID {produto_id}")
            
            # Listar produtos
            response = requests.get(f'{BASE_URL}/produtos')
            if response.status_code == 200:
                produtos = response.json()
                print(f"✅ Listagem de produtos: {len(produtos)} produtos")
            
            # Buscar produto
            response = requests.get(f'{BASE_URL}/produtos?q=Teste')
            if response.status_code == 200:
                produtos_busca = response.json()
                print(f"✅ Busca de produtos: {len(produtos_busca)} resultados")
            
            # Editar produto
            produto_data['descricao'] = "Teste Produto Editado"
            response = requests.put(f'{BASE_URL}/produtos/{produto_id}', json=produto_data)
            if response.status_code == 200:
                print("✅ Produto editado")
            
            # Excluir produto
            response = requests.delete(f'{BASE_URL}/produtos/{produto_id}')
            if response.status_code == 200:
                print("✅ Produto excluído")
            
            return True
        else:
            print(f"❌ Erro ao criar produto: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de produtos: {e}")
        return False

def testar_estabelecimentos():
    """Testa CRUD de estabelecimentos"""
    print("\n🏪 Testando estabelecimentos...")
    
    estabelecimento_data = {
        "nome": "Teste Mercado",
        "cnpj": "12345678901234",
        "bairro": "Centro",
        "cidade": "São Paulo"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/estabelecimentos', json=estabelecimento_data)
        if response.status_code == 201:
            estab_id = response.json()['id']
            print(f"✅ Estabelecimento criado com ID {estab_id}")
            
            # Listar estabelecimentos
            response = requests.get(f'{BASE_URL}/estabelecimentos')
            if response.status_code == 200:
                estabelecimentos = response.json()
                print(f"✅ Listagem de estabelecimentos: {len(estabelecimentos)} estabelecimentos")
            
            # Excluir estabelecimento
            response = requests.delete(f'{BASE_URL}/estabelecimentos/{estab_id}')
            if response.status_code == 200:
                print("✅ Estabelecimento excluído")
            
            return True
        else:
            print(f"❌ Erro ao criar estabelecimento: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de estabelecimentos: {e}")
        return False

def testar_precos():
    """Testa CRUD de preços"""
    print("\n💰 Testando preços...")
    
    # Primeiro criar produto e estabelecimento
    produto_data = {"descricao": "Produto Teste Preço", "ean": "1111111111111"}
    estab_data = {"nome": "Mercado Teste", "bairro": "Centro", "cidade": "SP"}
    
    try:
        # Criar produto
        response = requests.post(f'{BASE_URL}/produtos', json=produto_data)
        produto_id = response.json()['id']
        
        # Criar estabelecimento
        response = requests.post(f'{BASE_URL}/estabelecimentos', json=estab_data)
        estab_id = response.json()['id']
        
        # Criar preço
        preco_data = {
            "produto_id": produto_id,
            "estabelecimento_id": estab_id,
            "preco": 10.50
        }
        
        response = requests.post(f'{BASE_URL}/precos', json=preco_data)
        if response.status_code == 201:
            preco_id = response.json()['id']
            print(f"✅ Preço criado com ID {preco_id}")
            
            # Listar preços detalhados
            response = requests.get(f'{BASE_URL}/precos/detalhados')
            if response.status_code == 200:
                precos = response.json()
                print(f"✅ Listagem de preços detalhados: {len(precos['precos'])} preços")
            
            # Testar comparação
            response = requests.get(f'{BASE_URL}/comparar/{produto_id}')
            if response.status_code == 200:
                comparacao = response.json()
                print(f"✅ Comparação de preços: {len(comparacao['precos'])} preços encontrados")
            
            # Limpar dados de teste
            requests.delete(f'{BASE_URL}/precos/{preco_id}')
            requests.delete(f'{BASE_URL}/produtos/{produto_id}')
            requests.delete(f'{BASE_URL}/estabelecimentos/{estab_id}')
            print("✅ Dados de teste limpos")
            
            return True
        else:
            print(f"❌ Erro ao criar preço: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no teste de preços: {e}")
        return False

def testar_dashboard():
    """Testa endpoints do dashboard"""
    print("\n📊 Testando dashboard...")
    
    try:
        # Testar estatísticas
        response = requests.get(f'{BASE_URL}/dashboard/stats')
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Estatísticas: {stats['total_produtos']} produtos, {stats['total_estabelecimentos']} estabelecimentos, {stats['total_precos']} preços")
        
        # Testar produtos com preços
        response = requests.get(f'{BASE_URL}/produtos/com-precos')
        if response.status_code == 200:
            produtos_com_precos = response.json()
            print(f"✅ Produtos com preços: {len(produtos_com_precos)} produtos")
        
        return True
    except Exception as e:
        print(f"❌ Erro no teste de dashboard: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes das correções do PromoPreço")
    print("=" * 50)
    
    # Verificar se API está rodando
    if not testar_api():
        print("\n❌ API não está rodando. Execute 'python app.py' primeiro.")
        return
    
    # Aguardar um pouco para garantir que a API está pronta
    time.sleep(1)
    
    # Executar testes
    testes = [
        testar_produtos,
        testar_estabelecimentos,
        testar_precos,
        testar_dashboard
    ]
    
    sucessos = 0
    for teste in testes:
        if teste():
            sucessos += 1
    
    print("\n" + "=" * 50)
    print(f"📋 Resultado: {sucessos}/{len(testes)} testes passaram")
    
    if sucessos == len(testes):
        print("🎉 Todas as correções estão funcionando corretamente!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")

if __name__ == '__main__':
    main()