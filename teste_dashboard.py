#!/usr/bin/env python3
from app import app
from models import db, Produto, Estabelecimento, Preco

def teste_dashboard():
    with app.app_context():
        try:
            # Criar tabelas se não existirem
            db.create_all()
            
            # Testar contagens
            total_produtos = Produto.query.count()
            total_estabelecimentos = Estabelecimento.query.count()
            total_precos = Preco.query.count()
            
            print(f"✓ Produtos: {total_produtos}")
            print(f"✓ Estabelecimentos: {total_estabelecimentos}")
            print(f"✓ Preços: {total_precos}")
            print("✓ Dashboard stats funcionando!")
            
            return True
            
        except Exception as e:
            print(f"✗ Erro: {e}")
            return False

if __name__ == "__main__":
    teste_dashboard()