#!/usr/bin/env python3
"""
Script para verificar os dados no banco após população
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

def verificar_api():
    """Verifica se a API está funcionando"""
    try:
        response = requests.get(f'{BASE_URL}/api')
        return response.status_code == 200
    except:
        return False

def obter_estatisticas():
    """Obtém estatísticas do dashboard"""
    try:
        response = requests.get(f'{BASE_URL}/dashboard/stats')
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def listar_amostra(endpoint, nome, limite=5):
    """Lista uma amostra de dados"""
    try:
        response = requests.get(f'{BASE_URL}/{endpoint}')
        if response.status_code == 200:
            dados = response.json()
            print(f"\n📋 {nome} (mostrando {min(limite, len(dados))} de {len(dados)}):")
            
            for i, item in enumerate(dados[:limite]):
                if endpoint == 'produtos':
                    print(f"   {i+1}. {item['descricao']} (EAN: {item['ean']})")
                elif endpoint == 'estabelecimentos':
                    print(f"   {i+1}. {item['nome']} - {item['bairro']}, {item['cidade']}")
                elif endpoint == 'precos':
                    print(f"   {i+1}. Produto {item['produto_id']} - Estabelecimento {item['estabelecimento_id']} - R$ {item['preco']}")
            
            return len(dados)
        return 0
    except Exception as e:
        print(f"❌ Erro ao listar {nome}: {e}")
        return 0

def verificar_precos_por_produto():
    """Verifica quantos preços cada produto tem"""
    try:
        response = requests.get(f'{BASE_URL}/precos')
        if response.status_code == 200:
            precos = response.json()
            
            # Contar preços por produto
            precos_por_produto = {}
            for preco in precos:
                produto_id = preco['produto_id']
                precos_por_produto[produto_id] = precos_por_produto.get(produto_id, 0) + 1
            
            print(f"\n📊 Distribuição de preços:")
            print(f"   • Produtos com preços: {len(precos_por_produto)}")
            
            if precos_por_produto:
                min_precos = min(precos_por_produto.values())
                max_precos = max(precos_por_produto.values())
                media_precos = sum(precos_por_produto.values()) / len(precos_por_produto)
                
                print(f"   • Mín. preços por produto: {min_precos}")
                print(f"   • Máx. preços por produto: {max_precos}")
                print(f"   • Média preços por produto: {media_precos:.1f}")
            
            return True
        return False
    except Exception as e:
        print(f"❌ Erro ao verificar preços: {e}")
        return False

def main():
    print("🔍 Verificação dos dados no banco")
    print("=" * 40)
    
    # Verificar API
    if not verificar_api():
        print("❌ API não está respondendo")
        print("💡 Execute: python app.py")
        return
    
    print("✅ API está funcionando")
    
    # Obter estatísticas
    stats = obter_estatisticas()
    if stats:
        print(f"\n📊 Estatísticas Gerais:")
        totais = stats.get('totais', {})
        print(f"   • Produtos: {totais.get('produtos', 0)}")
        print(f"   • Estabelecimentos: {totais.get('estabelecimentos', 0)}")
        print(f"   • Preços: {totais.get('precos', 0)}")
        
        if stats.get('produto_mais_precos', {}).get('nome'):
            print(f"\n🏆 Produto com mais preços:")
            print(f"   • {stats['produto_mais_precos']['nome']} ({stats['produto_mais_precos']['total']} preços)")
        
        if stats.get('estabelecimento_mais_precos', {}).get('nome'):
            print(f"\n🏪 Estabelecimento com mais preços:")
            print(f"   • {stats['estabelecimento_mais_precos']['nome']} ({stats['estabelecimento_mais_precos']['total']} preços)")
    
    # Listar amostras
    total_produtos = listar_amostra('produtos', 'Produtos')
    total_estabelecimentos = listar_amostra('estabelecimentos', 'Estabelecimentos')
    total_precos = listar_amostra('precos', 'Preços')
    
    # Verificar distribuição de preços
    verificar_precos_por_produto()
    
    print(f"\n🎯 Resumo da Verificação:")
    print(f"   • Total de produtos: {total_produtos}")
    print(f"   • Total de estabelecimentos: {total_estabelecimentos}")
    print(f"   • Total de preços: {total_precos}")
    
    # Verificar se atingiu os objetivos
    objetivos_atingidos = (
        total_produtos >= 100 and 
        total_estabelecimentos >= 20 and 
        total_precos >= 1800  # Pelo menos 90% dos preços esperados
    )
    
    if objetivos_atingidos:
        print("✅ Objetivos de teste atingidos!")
    else:
        print("⚠️  Alguns objetivos não foram atingidos")
    
    print(f"\n🌐 Acesse o sistema em: {BASE_URL}")

if __name__ == '__main__':
    main()