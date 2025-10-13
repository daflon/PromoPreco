#!/usr/bin/env python3
"""
Script para resetar o banco e popular com dados de teste em uma única execução
"""

import subprocess
import sys
import os

def executar_comando(comando, descricao):
    """Executa comando e mostra resultado"""
    print(f"🔄 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descricao} concluído")
            return True
        else:
            print(f"❌ Erro em {descricao}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar {descricao}: {e}")
        return False

def main():
    print("🚀 Reset completo e população do banco de dados")
    print("=" * 50)
    
    # Mudar para diretório do projeto
    projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(projeto_dir)
    
    # 1. Reset do banco
    if not executar_comando("python force_reset.py", "Reset do banco de dados"):
        print("❌ Falha no reset. Abortando...")
        return
    
    # 2. Aguardar um pouco
    import time
    time.sleep(2)
    
    # 3. Popular com dados
    if not executar_comando("python Testes/popular_dados_completos.py", "População com dados de teste"):
        print("❌ Falha na população. Verifique se o Flask está rodando.")
        return
    
    print("\n🎉 Processo completo!")
    print("📊 Banco resetado e populado com:")
    print("   • 100 produtos")
    print("   • 20 estabelecimentos") 
    print("   • 2000 preços")
    print("\n💡 Dica: Execute 'python app.py' se não estiver rodando")

if __name__ == '__main__':
    main()