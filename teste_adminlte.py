#!/usr/bin/env python3
"""
Teste simples para verificar se o AdminLTE está funcionando
"""

import requests
import webbrowser
import time
import subprocess
import sys
import os

def verificar_servidor():
    """Verifica se o servidor Flask está rodando"""
    try:
        response = requests.get('http://localhost:5000/api', timeout=5)
        return response.status_code == 200
    except:
        return False

def iniciar_servidor():
    """Inicia o servidor Flask se não estiver rodando"""
    if not verificar_servidor():
        print("🚀 Iniciando servidor Flask...")
        # Executa o app.py em background
        subprocess.Popen([sys.executable, 'app.py'], 
                        cwd=os.path.dirname(os.path.abspath(__file__)))
        
        # Aguarda o servidor iniciar
        for i in range(10):
            time.sleep(1)
            if verificar_servidor():
                print("✅ Servidor Flask iniciado com sucesso!")
                return True
            print(f"⏳ Aguardando servidor... ({i+1}/10)")
        
        print("❌ Falha ao iniciar o servidor")
        return False
    else:
        print("✅ Servidor Flask já está rodando!")
        return True

def testar_adminlte():
    """Testa o dashboard AdminLTE"""
    print("\n🧪 Testando AdminLTE Dashboard...")
    
    if not iniciar_servidor():
        return False
    
    # URLs para testar
    urls = [
        ('http://localhost:5000/api', 'API Status'),
        ('http://localhost:5000/dashboard/stats', 'Dashboard Stats'),
        ('http://localhost:5000/dashboard/adminlte', 'AdminLTE Dashboard')
    ]
    
    print("\n📊 Testando endpoints:")
    for url, nome in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {nome}: OK")
            else:
                print(f"❌ {nome}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {nome}: Erro - {str(e)}")
    
    # Abrir o dashboard AdminLTE no navegador
    print("\n🌐 Abrindo AdminLTE Dashboard no navegador...")
    webbrowser.open('http://localhost:5000/dashboard/adminlte')
    
    print("\n✨ Teste concluído!")
    print("📋 O que você deve ver no AdminLTE:")
    print("   • Interface moderna com sidebar escura")
    print("   • Cards com estatísticas (produtos, estabelecimentos, preços)")
    print("   • Seção de comparação de preços")
    print("   • Busca de produtos com autocomplete")
    print("   • Toasts de notificação")
    print("   • Design responsivo")
    
    return True

if __name__ == '__main__':
    print("🎯 Teste do AdminLTE Dashboard - PromoPreço")
    print("=" * 50)
    
    try:
        testar_adminlte()
        
        print("\n💡 Dicas:")
        print("   • Acesse: http://localhost:5000/dashboard/adminlte")
        print("   • Compare com: http://localhost:5000/dashboard (versão original)")
        print("   • Use Ctrl+C para parar o servidor")
        
    except KeyboardInterrupt:
        print("\n\n👋 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {str(e)}")